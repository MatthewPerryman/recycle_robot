# Code from https://www.codingame.com/playgrounds/38470/how-to-detect-circles-in-images

from PIL import Image, ImageDraw
from math import pi, cos, sin, inf
from ImgProcessing.canny import canny_edge_detector
from collections import defaultdict


class CannyScrewCenter:
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
	def find_center(self, patch, from_file=False):
		# Output image:
		output_patch = Image.fromarray(patch)
		draw_result = ImageDraw.Draw(output_patch)

		points = []
		# Calculate possible points on the circumference of circles in the range of radii
		for r in range(self.rmin, self.rmax + 1):
			for t in range(self.steps):
				points.append((r, int(r * cos(2 * pi * t / self.steps)), int(r * sin(2 * pi * t / self.steps))))

		acc = defaultdict(int)
		# Obtains the strongest edges within the image
		# Calculate the difference between edge points and circle points
		for x, y in canny_edge_detector(Image.fromarray(patch)):
			for r, dx, dy in points:
				a = x - dx
				b = y - dy
				acc[(a, b, r)] += 1

		# Circles centre x, y coordinates and radius
		circles = [inf, inf, inf]
		# Only keep circles with > 40% of points on the edge points of the screw
		# AND Circles with centres within the radius of an existing circle.
		for k, v in sorted(acc.items(), key=lambda i: -i[1]):
			x, y, r = k
			# and (x - circles[1]) ** 2 + (y - circles[1]) ** 2 > circles[2] ** 2
			# Keep the smallest radius circle
			if v / self.steps >= self.threshold and r < circles[2]:
				print(v / self.steps, x, y, r)
				circles = [x, y, r]

		# Draw the circle and centre coordinate on an image
		x, y, r = circles[0], circles[1], circles[2]

		draw_result.ellipse((x - r, y - r, x + r, y + r), outline=(255, 0, 0, 0))
		draw_result.point([(x, y)], fill="blue")
		draw_result.point([(x + 1, y)], fill="blue")
		draw_result.point([(x, y + 1)], fill="blue")
		draw_result.point([(x + 1, y + 1)], fill="blue")

		# Debug
		output_patch.show()
		if from_file:
			# Save output image
			output_patch.show()

			return output_patch
		else:
			# In test, it's assumed only one screw is in the patch
			return [circles[0], circles[1]]
