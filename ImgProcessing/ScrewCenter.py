# Code from https://www.codingame.com/playgrounds/38470/how-to-detect-circles-in-images

from PIL import Image, ImageDraw
from math import sqrt, pi, cos, sin
from canny import canny_edge_detector
from collections import defaultdict

class CannyScrewCenter():
	# Search parameters
	rmin = 20
	rmax = 50
	steps = 100
	threshold = 0.4
	
	def load_from_PNG(self):
		# Load image:
		circled_n_centered = self.FindCenter(Image.open("FirstImgScew.png"))
		# Write circled_n_centered to file maybe

	def find_center(self, patch, from_file = False):
		# Output image:
		output_patch = Image.new("RGB", patch.size)
		output_patch.paste(patch)
		draw_result = ImageDraw.Draw(output_patch)

		points = []
		for r in range(self.rmin, self.rmax + 1):
			for t in range(self.steps):
				points.append((r, int(r * cos(2 * pi * t / self.steps)), int(r * sin(2 * pi * t / self.steps))))

		acc = defaultdict(int)
		for x, y in canny_edge_detector(patch):
			for r, dx, dy in points:
				a = x - dx
				b = y - dy
				acc[(a, b, r)] += 1

		circles = []
		for k, v in sorted(acc.items(), key=lambda i: -i[1]):
			x, y, r = k
			if v / self.steps >= self.threshold and all((x - xc) ** 2 + (y - yc) ** 2 > rc ** 2 for xc, yc, rc in circles):
				print(v / self.steps, x, y, r)
				circles.append((x, y, r))

		for x, y, r in circles:
			draw_result.ellipse((x - r, y - r, x + r, y + r), outline=(255, 0, 0, 0))
			draw_result.point([(x, y)], fill="blue")
			draw_result.point([(x+1, y)], fill="blue")
			draw_result.point([(x, y+1)], fill="blue")
			draw_result.point([(x+1, y+1)], fill="blue")

		if from_file:
			# Save output image
			output_patch.show()

			return output_patch
		else:
			# In test, it's assumed only one screw is in the patch
			return [circles[0][0], circles[0][1]]
