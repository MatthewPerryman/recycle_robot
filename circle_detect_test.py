import cv2
import numpy as np

image = cv2.imread("C:/Users/matth/Documents/gitrepos/recycle_robot/patch.png")
output = image.copy()
grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# hist = cv2.equalizeHist(grey)
# blur = cv2.GaussianBlur(hist, (1, 1), cv2.BORDER_DEFAULT)
cv2.imshow("grey", grey)
cv2.waitKey(0)

# Find circles
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
# show the output image
cv2.imshow("circle", output)
cv2.waitKey(0)
cv2.destroyAllWindows()
