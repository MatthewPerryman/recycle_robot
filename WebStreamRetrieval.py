# Importing Required Modules
import cv2
import requests
import numpy as np
from Model.detect import Classifier
from ImgProcessing.ScrewCenter import CannyScrewCenter
from absl import app, logging
import time
import math
import json

Canny = CannyScrewCenter()

# Note: all coordinates are x, y
image_shape = (640, 480, 3)
m_frame_distance = (0, 0, -10)

# Find the center pixel in the image
center_pixel = (image_shape[1] / 2, image_shape[0] / 2)

# Based upon datasheet https://cdn.sparkfun.com/datasheets/Dev/RaspberryPi/ov5647_full.pdf#:~:text=The%20OV5647%20is%20a%20low%20voltage%2C%20high%20performance%2C,the%20serial%20camera%20control%20bus%20or%20MIPI%20interface.
pixel_size = 0.0014  # (mm) = 1.4 micrometers

# (CMOS size - tot pixel size)/number of gaps (per axis)
pixel_gap_size_x = (5.52 - (pixel_size * 2592)) / 2591
pixel_gap_size_y = (4.7 - (pixel_size * 1944)) / 1943

# Vector from motor tip to camera
motor_to_camera = (-25, 0, 13)


def detect_screws_in_stream(model):
	while True:
		t1 = time.time()
		# Exception Handling for invalid requests
		try:
			c1 = time.time()
			# Creating an request object to store the response
			# The URL is referenced sys.argv[1]
			ImgRequest = requests.get("http://192.168.0.116:80/live_photo")
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
	box_height_extension = (bounding_box[1][0] - bounding_box[0][0]) // 2
	box_width_extension = (bounding_box[1][1] - bounding_box[0][1]) // 2

	# Define the corners of the image patch, top left and bottom right corners
	patch_top_left = (bounding_box[0][0] - box_height_extension, bounding_box[0][1] - box_width_extension)
	patch_bottom_right = (bounding_box[1][0] + box_height_extension, bounding_box[1][1] + box_width_extension)

	patch = image[patch_top_left[0]: patch_bottom_right[0], patch_top_left[1]: patch_bottom_right[1]]
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
		dist_to_center = math.hypot((bbx_center[0] - center_pixel[0]),
									(bbx_center[1] - center_pixel[1]))

		if dist_to_center < closest_to_center[2]:
			closest_to_center[0] = i
			closest_to_center[1] = bbx_center
			closest_to_center[2] = dist_to_center

	# Outputs the box score and corner coordinates
	logging.info('\tClosest: Score: {}, Coords: {}'.format(np.array(scores[0][closest_to_center[0]]),
														   np.array(bbxs[closest_to_center[0]])))

	# Return the closest boxes: index, top left and right coordinates, and hypot to centre
	return closest_to_center


def get_vector_to_screw(dist_to_center1, center_coord1, f_len, dist_to_center2):
	# Perpendicular Distance (d) from lens to laptop = distance moved (m (10mm)) / (1 - (Frame1Dist_to_Centre/Frame2Dist_to_Center
	d = 20 / (1 - (dist_to_center1 / dist_to_center2))

	# Distance from the camera in the z axis. Down is negative for these coordinates
	Zd = -d

	# Pixel x (Px) = (y axis distance between image center & box center * pixel size) + no. gaps between pixels * gap size
	# y axis label to match real world y and x
	pixel_diff = (center_pixel[0] - center_coord1[0], center_pixel[1] - center_coord1[1])
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
	try:
		# Creating an request object to store the response
		# The URL is referenced sys.argv[1]
		ImgRequest = requests.get("http://192.168.0.116:80/get_images_for_depth")
		if ImgRequest.status_code == requests.codes.ok:
			# Read numpy array bytes
			depth_dict = json.loads(ImgRequest.content)

			image1 = depth_dict['img1']
			f_len = depth_dict['f_len'] / 100
			image2 = depth_dict['img2']

			image1 = np.asarray(image1)
			image2 = np.asarray(image2)

			# Reshape image values into 640 x 480 x 3 image as needed
			image1 = np.reshape(image1, newshape=image_shape).astype(np.uint8)
			image2 = np.reshape(image2, newshape=image_shape).astype(np.uint8)

			# Locate and box the screws in both images
			output_img1, img_boxes1, scores1, nums1 = model.detect(image1)
			output_img2, img_boxes2, scores2, nums2 = model.detect(image2)

			if (int(nums1[0]) is not 0) and (int(nums2[0]) is not 0):
				# Just to check image quality even if not detection occurs
				cv2.imshow("Img1", output_img1)
				cv2.waitKey(0)
				cv2.imshow("Img2", output_img2)
				cv2.waitKey(0)

				if input("Proceed?: ") == 'n':
					cv2.destroyAllWindows()
					return False

				# Given at least one screw is detected, find the closest to the image center
				closest_box1 = find_closest_box(image1, nums1, img_boxes1, scores1)
				closest_box2 = find_closest_box(image2, nums2, img_boxes2, scores2)

				# Index, coords, dist_to_center
				bbx_center_1, dist_to_center1 = closest_box1[2], closest_box1[3]
				dist_to_center2 = closest_box2[3]

				motor_to_screw = get_vector_to_screw(dist_to_center1, bbx_center_1, f_len, dist_to_center2)

				print(requests.post("http://192.168.0.116:80/move_robot_to/", data=json.dumps(motor_to_screw)).content)

				return True
			else:
				print("Error: No object was detected in one of the frames")

			# cv2.imshow("Img1", output_img1)
			# cv2.waitKey(0)
			# cv2.imshow("Img2", output_img2)
			# cv2.waitKey(0)

			cv2.destroyAllWindows()

			return False
		else:
			print("Error: {}".format(ImgRequest.status_code))
			return False
	except Exception as e:
		print(str(e))


def main(_argv):
	Model = Classifier()

	# detect_screws_in_stream(Model)
	while True:
		if find_and_move_to_screw(Model):
			break


if __name__ == '__main__':
	try:
		app.run(main)
	except SystemExit:
		pass
