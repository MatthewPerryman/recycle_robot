import cv2  # sudo apt-get install python-opencv
import numpy as np
from ctypes import *
import sys
from time import sleep, time
from Utils import Logging

try:
	import picamera
	from picamera.array import PiRGBArray
except:
	sys.exit(0)


# Stock functions except __init__, __del__, and updated take_photo
class ImageStream():
	# load arducam shared object file
	arducam_vcm = CDLL('./Server_Package/PiCode/rpiWebServer/API/lib/libarducam_vcm.so')
	camera = None
	# Flipping resolution doesn't work
	resolution = (640, 480, 3)
	# second frame 10mm below first frame
	m_frame_distance = (0, 0, -20)

	def adjust_lens(self, val):
		self.arducam_vcm.vcm_write(val)

	def laplacian(self, img):
		img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
		img_sobel = cv2.Laplacian(img_gray, cv2.CV_16U)
		return cv2.mean(img_sobel)[0]

	def calculation(self, camera):
		rawCapture = PiRGBArray(camera)
		self.camera.capture(rawCapture, format="bgr", use_video_port=True)
		image = rawCapture.array
		rawCapture.truncate(0)
		return self.laplacian(image)

	# Runs through all lense focal lengths until clarity reduces, then sets length to best length
	def focus(self):
		print("Start focusing")

		self.max_index = 10
		self.max_value = 0.0
		self.last_value = 0.0
		self.dec_count = 0
		self.focal_distance = 10

		while True:
			# Adjust focus
			self.adjust_lens(self.focal_distance)
			# Take image and calculate image clarity
			val = self.calculation(self.camera)
			# Find the maximum image clarity
			if val > self.max_value:
				self.max_index = self.focal_distance
				self.max_value = val

			# If the image clarity starts to decrease
			if val < self.last_value:
				self.dec_count += 1
			else:
				self.dec_count = 0
			# Image clarity is reduced by six consecutive frames
			if self.dec_count > 6:
				break
			self.last_value = val

			# Increase the focal distance
			self.focal_distance += 15
			if self.focal_distance > 1000:
				break

		# Adjust focus to the best
		self.adjust_lens(self.max_index)
		print('Focussed')

	def capture_photo(self):
		# Create image array
		image_array = np.empty(self.resolution, dtype=np.uint8)

		# Capture image to np array
		self.camera.capture(image_array, 'rgb')

		return image_array

	# Returns a captured photo
	# Does not refocus before shot
	# TODO: (This needs updating when camera motorised in the Z axis!)
	def take_photo(self):
		self.cam_open()

		image_array = self.capture_photo()

		self.camera.close()

		# Returns image in numpy array format.
		return image_array

	def get_imgs_for_depth(self, arm_move_function, write_log):
		Logging.write_log("server", "Open camera")
		self.cam_open()

		sleep(1)
		# Capture image 1
		Logging.write_log("server", "First Photo")
		img1 = self.capture_photo()

		# Get the f_len of the first image
		focal_len = self.max_index

		# Move the robot up 10mm
		Logging.write_log("server", "Move Arm 1")
		arm_move_function(self.m_frame_distance)

		# Refocus for new location
		Logging.write_log("server", "Focus Camera in New Location")
		self.focus()

		sleep(1)
		# Capture image 2
		Logging.write_log("server", "Second Photo")
		img2 = self.capture_photo()

		# Reset focus for position 1
		Logging.write_log("server", "Move Arm 2")
		self.max_index = focal_len
		arm_move_function(self.m_frame_distance, reverse_vector=True)

		self.camera.close()

		Logging.write_log("server", "Return from image_stream get depth images")
		return img1, focal_len, img2

	def cam_open(self):
		# Open camera - Set camera resolution to 480x640(Small resolution for faster speeds.)
		# Camera needs a flipped resolution
		self.camera = picamera.PiCamera(resolution=(self.resolution[1], self.resolution[0]))

		# self.camera.shutter_speed = 30000

		# https://picamera.readthedocs.io/en/release-1.13/recipes1.html?highlight=shutter%20speed#capturing-consistent-images
		self.camera.iso = 100
		# Wait for the automatic gain control to settle
		sleep(2)

		self.camera.shutter_speed = self.camera.exposure_speed
		# To fix exposure gains, let analog_gain and digital_gain settle on reasonable values, then set exposure_mode to 'off'. (from doc)
		self.camera.exposure_mode = 'off'

		# To fix white balance, set the awb_mode to 'off', then set awb_gains to a (red, blue) tuple of gains.(from doc)
		g = self.camera.awb_gains
		self.camera.awb_mode = 'off'
		self.camera.awb_gains = g

		# Adjust focus to the best
		self.adjust_lens(self.max_index)

	# Close camera after use in next function

	def __init__(self):
		# vcm init
		self.arducam_vcm.vcm_init()

		# open camera
		self.camera = picamera.PiCamera(resolution=(self.resolution[1], self.resolution[0]))

		# set camera resolution to 640x480(Small resolution for faster speeds.)
		# self.camera.resolution = (self.resolution[1], self.resolution[0])
		# time.sleep(0.1)
		self.camera.shutter_speed = 30000

		# Determine focus values
		# Using this class in a Flask app runs init twice therefore self.camera.close() is needed
		self.focus()

		# Clear up
		self.camera.close()

	def __del__(self):
		self.camera.close()
