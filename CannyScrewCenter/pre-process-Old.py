import os
import numpy as np
import cv2
import copy
import matplotlib.pyplot as plt

laptop_img = cv2.imread("C:/Users/matth/Documents/gitrepos/recycle_robot/LabelledImages/vott-json-export/img0.jpg",
						cv2.IMREAD_COLOR)

hist_img = copy.copy(laptop_img)

# equalize the histogram of the R, G, and B channels
hist_img[:, :, 0] = cv2.equalizeHist(hist_img[:, :, 0])
hist_img[:, :, 1] = cv2.equalizeHist(hist_img[:, :, 1])
hist_img[:, :, 2] = cv2.equalizeHist(hist_img[:, :, 2])

hist_img = cv2.cvtColor(hist_img, cv2.COLOR_BGR2YUV)
hist_img = cv2.cvtColor(hist_img, cv2.COLOR_YUV2BGR)

cv2.imshow("Histogram Equalised", hist_img)
cv2.imshow("Laptop", laptop_img)

cv2.waitKey(0)  # waits until a key is pressed
cv2.destroyAllWindows()  # destroys the window showing image
