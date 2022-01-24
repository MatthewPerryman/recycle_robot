# Importing Required Modules
import cv2
import requests
import numpy as np
from absl import app, logging
from time import time
import math
import io
import json
from string import Template
from PIL import Image as im

from Model.detect import Classifier
from CannyScrewCenter.ScrewCenter import CannyScrewCenter
from Utils import Logging

IMG_LABELS_FILE = "Autogathered_Dataset/img_labels.json"

Canny = CannyScrewCenter()

# Note: all coordinates are x, y
image_shape = (640, 480, 3)
m_frame_distance = (0, 0, -10)

# Find the center pixel in the image
image_center = (image_shape[1] / 2, image_shape[0] / 2)

# Based upon datasheet https://cdn.sparkfun.com/datasheets/Dev/RaspberryPi/ov5647_full.pdf#:~:text=The%20OV5647%20is%20a%20low%20voltage%2C%20high%20performance%2C,the%20serial%20camera%20control%20bus%20or%20MIPI%20interface.
pixel_size = 0.0014  # (mm) = 1.4 micrometers

# (CMOS size - tot pixel size)/number of gaps (per axis)
pixel_gap_size_x = (5.52 - (pixel_size * 2592)) / 2591
pixel_gap_size_y = (4.7 - (pixel_size * 1944)) / 1943

# Vector from motor tip to camera
motor_to_camera = (-25, -2, 23)

sign = lambda a: (a > 0) - (a < 0)
mag = lambda a: a * sign(a)


def detect_screws_in_stream(model):
	while True:
		t1 = time()
		# Exception Handling for invalid requests
		try:
			c1 = time()
			# Creating an request object to store the response
			# The URL is referenced sys.argv[1]
			ImgRequest = requests.get("http://192.168.0.116:80/get_photo")
			# Verifying whether the specified URL exist or not
			if ImgRequest.status_code == requests.codes.ok:
				# Read numpy array bytes
				image = np.frombuffer(ImgRequest.content, dtype=np.uint8)

				# Reshape image values into 640 x 480 x 3 image as needed
				image = np.reshape(image, newshape=image_shape)
				c2 = time.time()
				t2 = time.time()

				# Display the labelled image with a delay of 1 millisecond (minimum delay)
				output_img, bbxs, scores, nums = model.detect(image)

				if int(nums[0]) is not 0:
					closest_box, _, _ = find_closest_box(nums, bbxs, scores)

				cv2.imshow("Laptop", output_img)
				cv2.waitKey(1)
			else:
				print("Error: {}".format(ImgRequest.status_code))

			logging.info('Call API time: {}'.format(c2 - c1))
			logging.info('Full loop time: {}'.format(t2 - t1))
		except Exception as e:
			print(str(e))


# Returns the patch of the input image that contains the bounding box + extension
def get_patch(image, bounding_box):
	# Get each boxes height and width to build a patch twice as large
	box_height_extension = (bounding_box[1][1] - bounding_box[0][1]) // 2
	box_width_extension = (bounding_box[1][0] - bounding_box[0][0]) // 2

	# Define the corners of the image patch, top left and bottom right corners
	patch_top_left = (bounding_box[0][0] - box_width_extension, bounding_box[0][1] - box_height_extension)
	patch_bottom_right = (bounding_box[1][0] + box_width_extension, bounding_box[1][1] + box_height_extension)

	# Bbx (x,y), array lookup (y, x)
	patch = image[patch_top_left[1]: patch_bottom_right[1], patch_top_left[0]: patch_bottom_right[0]]
	return patch, (patch_top_left, patch_bottom_right)


def patch_n_find_center(image, bbx):
	patch, patch_coords = get_patch(image, bbx)

	## Pass patches to a canny edge detector to find the center of the screws
	patch_center = Canny.find_center(patch)

	return patch_center, patch_coords


# Find closest object to the center of the image
def find_closest_box(image, nums, bbxs, scores):
	# Store the index and distance of the closest box to the center - last 2 are y errored values
	closest_to_center = [0, (0, 0), math.inf, (0, 0), 0]
	for i in range(nums[0]):
		# Boxes: [[(x0, y0), (x3, y3)]]

		# Create a patch around the bounding box, use canny to find center
		patch_center, patch_coords = patch_n_find_center(image, bbxs[i])

		# Convert patch coordinate to image coordinate
		bbx_center = (patch_coords[0][0] + patch_center[0], patch_coords[0][1] + patch_center[1])

		# Find the box center closest to the image center
		dist_to_center = math.hypot((bbx_center[0] - image_center[0]),
									(bbx_center[1] - image_center[1]))

		if dist_to_center < closest_to_center[2]:
			closest_to_center[0] = i
			closest_to_center[1] = bbx_center
			closest_to_center[2] = dist_to_center

	# Outputs the box score and corner coordinates
	logging.info('\tClosest: Score: {}, Coords: {}'.format(np.array(scores[0][closest_to_center[0]]),
														   np.array(bbxs[closest_to_center[0]])))

	# Return the closest boxes: index, top left and right coordinates, and hypot to centre
	return closest_to_center


def get_vector_to_screw(dist_to_center1, screw_center1, f_len, dist_to_center2):
	# Perpendicular Distance (d) from lens to laptop = distance moved (m (10mm)) / (1 - (Frame1Dist_to_Centre/Frame2Dist_to_Center
	d = 20 / (1 - (dist_to_center1 / dist_to_center2))

	# Distance from the camera in the z axis. Down is negative for these coordinates
	Zd = -d

	# Pixel x (Px) = (y axis distance between image center & box center * pixel size) + no. gaps between pixels * gap size
	# y axis label to match real world y and x
	pixel_diff = (image_center[0] - screw_center1[0], image_center[1] - screw_center1[1])
	Px = (pixel_diff[1] * pixel_size) + ((pixel_diff[1] - 1) * pixel_gap_size_y)
	# Pixel y (Py) same as above but with x axis distance
	Py = (pixel_diff[0] * pixel_size) + ((pixel_diff[0] - 1) * pixel_gap_size_x)

	# Ratio, divide x&y by focal length, multiply by real world distance
	Xd = (Zd * Px) / f_len
	Yd = (Zd * Py) / f_len

	camera_to_screw = (Xd, Yd, Zd)

	# Vector arithmetic to get from a to c via b
	motor_to_screw = {'Xd': camera_to_screw[0] + motor_to_camera[0],
					  'Yd': camera_to_screw[1] + motor_to_camera[1],
					  'Zd': camera_to_screw[2] + motor_to_camera[2]}

	return motor_to_screw


def find_and_move_to_screw(model):
	moving_to_screw = False
	while (not moving_to_screw):
		Logging.write_log("client", "\nNew Run:\n")
		try:
			# Creating an request object to store the response
			# The URL is referenced sys.argv[1]

			ImgRequest = requests.get("http://192.168.0.116:80/get_images_for_depth")
			Logging.write_log("client", "Received Images from Server")

			if ImgRequest.status_code == requests.codes.ok:
				# Read numpy array bytes
				np_zfile = np.load(io.BytesIO(ImgRequest.content))

				image1 = np_zfile['arr_0']
				f_len = np_zfile['arr_1'] / 100  # To mm
				image2 = np_zfile['arr_2']

				# Locate and box the screws in both images
				output_img1, img_boxes1, scores1, nums1 = model.detect(image1)
				output_img2, img_boxes2, scores2, nums2 = model.detect(image2)

				if (int(nums1[0]) is not 0) and (int(nums2[0]) is not 0):
					# Just to check image quality
					cv2.imshow("Img1", output_img1)
					cv2.waitKey(0)
					cv2.imshow("Img2", output_img2)
					cv2.waitKey(0)

					if input("Proceed?: ") == 'y':
						# Given at least one screw is detected, find the closest to the image center
						closest_box1 = find_closest_box(image1, nums1, img_boxes1, scores1)
						closest_box2 = find_closest_box(image2, nums2, img_boxes2, scores2)

						# Index, coords, dist_to_center
						bbx_center_1, dist_to_center1 = closest_box1[1], closest_box1[2]
						dist_to_center2 = closest_box2[2]

						motor_to_screw = get_vector_to_screw(dist_to_center1, bbx_center_1, f_len, dist_to_center2)

						print(requests.post("http://192.168.0.116:80/move_by_vector/",
											data=json.dumps(motor_to_screw)).content)
						moving_to_screw = True
					else:
						cv2.destroyAllWindows()
				else:
					print("Error: No object was detected in one of the frames")

				cv2.destroyAllWindows()
			else:
				print("Error: {}".format(ImgRequest.status_code))
		except Exception as e:
			print(str(e))


def get_photo():
	ImgRequest = requests.get("http://192.168.0.116:80/get_photo")
	Logging.write_log("client", "Received Image from Server")

	if ImgRequest.status_code == requests.codes.ok:
		# Read numpy array bytes
		np_zfile = np.load(io.BytesIO(ImgRequest.content))

		image = np_zfile['arr_0']

		return image


def try_annotate_and_save_image(model, image, laptop_id, image_id):
	annotation_id = image_id
	image_name = "Autogathered_Dataset/" + str((laptop_id * 1000) + image_id) + ".png"
	# Save image
	img_data = im.fromarray(image)
	img_data.save(image_name)

	# If any objects are detected, save the boudning box numbers in a file associated with the image
	output_img, img_boxes, scores, nums = model.detect(image)

	if int(nums[0]) is not 0:
		# Read in from output file
		with open(IMG_LABELS_FILE, "r") as labels_file:
			labels_data = json.load(labels_file)

		for i in range(nums[0]):
			# Prepare values for populating entry
			box_area = int(abs(img_boxes[i][1][0] - img_boxes[i][0][0]) * abs(img_boxes[i][1][1] - img_boxes[i][0][1]))

			detected_values = {	"id": annotation_id,
								"image_id": (laptop_id * 1000) + image_id,
								"category_id": 1,
								"bbox": [[int(img_boxes[i][0][0]), int(img_boxes[i][0][1])],
										[int(img_boxes[i][1][0]), int(img_boxes[i][1][1])]],
								"bbox_area": box_area}

			labels_data["annotations"].append(detected_values)

		# Prepare values for populating entry
		image_values = {"id": (laptop_id * 1000) + image_id,
						"filename": image_name,
						"img_height": image_shape[1],
						"img_width": image_shape[0]}

		# Add image json
		labels_data["images"].append(image_values)

		# Write to output file
		with open(IMG_LABELS_FILE, "w") as labels_file:
			json.dump(labels_data, labels_file)
	else:
		# Read in from output file
		with open(IMG_LABELS_FILE, "r") as labels_file:
			labels_data = json.load(labels_file)

			# Prepare values for populating entry
			image_values = {"id": image_id,
							"filename": image_name,
							"img_height": image_shape[1],
							"img_width": image_shape[0]}

		# Add image json
		labels_data["images"].append(image_values)

		# Write to output file
		with open(IMG_LABELS_FILE, "w") as labels_file:
			json.dump(labels_data, labels_file)


def fetch_label_store(model, laptop_id):
	image_id = 0

	direction = -1
	photo_gap = 10

	x_value = 150
	x_move_complete = True
	y_value = 120
	y_limit = 120

	requests.post("http://192.168.0.116:80/set_position/",
				  data=bytes(json.dumps({'Xd': x_value, 'Yd': y_value, 'Zd': 150}), 'utf-8'))

	# Take photo
	image = get_photo()

	try_annotate_and_save_image(model, image, laptop_id, image_id)

	scan_complete = False
	while not scan_complete:
		image_id += 1
		x_delta = 0
		y_delta = 0

		try:
			# Keep moving along the line
			if mag(y_value + (direction * photo_gap)) <= y_limit:
				y_value += direction * photo_gap
				y_delta = direction * photo_gap

				MoveResponse = requests.post("http://192.168.0.116:80/move_by_vector/",
											 data=bytes(json.dumps({'Xd': x_delta, 'Yd': y_delta, 'Zd': 0}), 'utf-8'))
				if json.loads(MoveResponse.content)['response']:
					print("Successful Move")
			else:  # Move up x-axis, change direction
				x_value += photo_gap
				x_delta = photo_gap
				direction = -direction

				moved_in_x = False
				while not moved_in_x:
					Logging.write_log("client", "Attempt Move Robot")

					MoveResponse = requests.post("http://192.168.0.116:80/move_by_vector/",
												 data=bytes(json.dumps({'Xd': x_delta, 'Yd': y_delta, 'Zd': 0}),
															'utf-8'))
					if json.loads(MoveResponse.content)['response']:
						moved_in_x = True
					else:
						# If not passed y center, move further towards center
						if sign(direction) is not sign(y_value) and mag(y_value + (direction * photo_gap)) <= y_limit:
							y_value += direction * photo_gap
							y_delta = direction * photo_gap
						# Crossed y=0 and cannot move forward in x means reached far side
						elif sign(direction) == sign(y_value) and mag(y_value + (direction * photo_gap)) <= y_limit:
							scan_complete = True
							break
			if not scan_complete:
				# Take photo
				image = get_photo()

				try_annotate_and_save_image(model, image, laptop_id, image_id)

		except Exception as e:
			print(str(e))


def find_robot_limit():
	cmd_success = True
	axis = 'x'
	direction = -1
	increment = 1
	y_limit = 120
	# Not necessary
	x_limit = 150

	requests.post("http://192.168.0.116:80/set_position/",
				  data=bytes(json.dumps({'Xd': 150, 'Yd': 0, 'Zd': 150}), 'utf-8'))

	while cmd_success:
		# @z=150 Closest x=150
		if axis == 'x':
			MoveResponse = requests.post("http://192.168.0.116:80/move_by_vector/",
										 data=bytes(json.dumps({'Xd': direction * 1, 'Yd': 0, 'Zd': 0}), 'utf-8'))
		# @z=150 Left most y =
		elif axis == 'y':
			MoveResponse = requests.post("http://192.168.0.116:80/move_by_vector/",
										 data=bytes(json.dumps({'Xd': 0, 'Yd': direction * 1, 'Zd': 0}), 'utf-8'))
		elif axis == 'z':
			MoveResponse = requests.post("http://192.168.0.116:80/move_by_vector/",
										 data=bytes(json.dumps({'Xd': 0, 'Yd': 0, 'Zd': direction * 1}), 'utf-8'))
		increment += 1

		if MoveResponse.content != bytes('Move Successful: False', 'utf-8') and increment <= y_limit:
			cmd_success = True
		else:
			cmd_success = False

			MoveResponse = requests.get("http://192.168.0.116:80/get_position/")
			print("Last Successful Move: {}".format(MoveResponse.content))


def main(_argv):
	Model = Classifier()
	laptop_id = 1
	another_laptop = True

	# detect_screws_in_stream(Model)
	# find_and_move_to_screw(Model)
	# find_robot_limit()
	while another_laptop:
		fetch_label_store(Model, laptop_id)
		if input("Scan Another Laptop?: ") == 'Y' or input("Scan Another Laptop?: ") == 'y':
			laptop_id += 1
			another_laptop = True
		else:
			another_laptop = False


if __name__ == '__main__':
	try:
		app.run(main)
	except SystemExit:
		pass
