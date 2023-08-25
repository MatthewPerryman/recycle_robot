# Code from https://www.codingame.com/playgrounds/38470/how-to-detect-circles-in-images
import cv2
import numpy as np
from PIL import Image, ImageDraw
from math import pi, cos, sin, inf
from FindCentrewithCanny.canny import canny_edge_detector
from collections import defaultdict


class CannyScrewCentre:
	# Search parameters
	rmin = 10
	rmax = 50
	steps = 100
	threshold = 0.6

	def load_from_png(self):
		# Load image:
		circled_n_centered = self.find_center(Image.open("FirstImgScew.png"))
		return circled_n_centered

	# Write circled_n_centered to file maybe
	def find_center(self, patch, from_file=True):
		output = patch.copy()
		grey = cv2.cvtColor(patch, cv2.COLOR_BGR2GRAY)

		# hist = cv2.equalizeHist(grey)
		# blur = cv2.GaussianBlur(hist, (3, 3), cv2.BORDER_DEFAULT)

		# Find circles (hacky values)
		circles = cv2.HoughCircles(grey, cv2.HOUGH_GRADIENT, 1, 200,
								   param1=40, param2=20, minRadius=5, maxRadius=30)
		# If some circle is found
		if circles is not None:
			# Get the (x, y, r) as integers
			circles = np.round(circles[0, :]).astype("int")
			print(circles)
			# loop over the circles
			for (x, y, r) in circles:
				cv2.circle(output, (x, y), r, (0, 255, 0), 2)

		# Debug
		cv2.imshow("circle", output)
		cv2.waitKey(0)
		if from_file:
			# Save output image
			cv2.imwrite("C:/Users/matth/Documents/gitrepos/recycle_robot/patch.png", output)

			return [circles[0][0], circles[0][1]]
		else:
			# In test, it's assumed only one screw is in the patch
			return [circles[0][0], circles[0][1]]
