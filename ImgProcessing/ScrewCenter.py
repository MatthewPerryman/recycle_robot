# Code from https://www.codingame.com/playgrounds/38470/how-to-detect-circles-in-images

from PIL import Image, ImageDraw
from math import sqrt, pi, cos, sin
from canny import canny_edge_detector
from collections import defaultdict

# Load image:
input_image = Image.open("FirstImgScew.png")

# Output image:
output_image = Image.new("RGB", input_image.size)
output_image.paste(input_image)
draw_result = ImageDraw.Draw(output_image)

# Find circles
rmin = 20
rmax = 50
steps = 100
threshold = 0.4

points = []
for r in range(rmin, rmax + 1):
	for t in range(steps):
		points.append((r, int(r * cos(2 * pi * t / steps)), int(r * sin(2 * pi * t / steps))))

acc = defaultdict(int)
for x, y in canny_edge_detector(input_image):
	for r, dx, dy in points:
		a = x - dx
		b = y - dy
		acc[(a, b, r)] += 1

circles = []
for k, v in sorted(acc.items(), key=lambda i: -i[1]):
	x, y, r = k
	if v / steps >= threshold and all((x - xc) ** 2 + (y - yc) ** 2 > rc ** 2 for xc, yc, rc in circles):
		print(v / steps, x, y, r)
		circles.append((x, y, r))

for x, y, r in circles:
	draw_result.ellipse((x - r, y - r, x + r, y + r), outline=(255, 0, 0, 0))
	draw_result.point([(x, y)], fill="blue")
	draw_result.point([(x+1, y)], fill="blue")
	draw_result.point([(x, y+1)], fill="blue")
	draw_result.point([(x+1, y+1)], fill="blue")

# Save output image
output_image.show()
