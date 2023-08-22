import cv2
from absl import app
import numpy as np
import copy

repo_pwd = "C:/Users/drago/Documents/gitrepos/recycle_robot/"

def main(_argv):
	print(repo_pwd + "Autogathered_Dataset/1/Original_images/0.png")
	laptop_img = cv2.imread(repo_pwd + "Autogathered_Dataset/1/Original_images/0.png",
							cv2.IMREAD_COLOR)
	print(type(laptop_img))
	hist_img = copy.deepcopy(laptop_img)
	print(hist_img.shape)

	# equalize the histogram of the R, G, and B channels
	hist_img[:, :, 0] = cv2.equalizeHist(hist_img[:, :, 0])
	hist_img[:, :, 1] = cv2.equalizeHist(hist_img[:, :, 1])
	hist_img[:, :, 2] = cv2.equalizeHist(hist_img[:, :, 2])

	# hist_img = cv2.cvtColor(hist_img, cv2.COLOR_BGR2YUV)
	# hist_img = cv2.cvtColor(hist_img, cv2.COLOR_YUV2BGR)

	cv2.imshow("Histogram Equalised", hist_img)
	cv2.imshow("Laptop", laptop_img)

	cv2.waitKey(0)  # waits until a key is pressed
	cv2.destroyAllWindows()  # destroys the window showing image

if __name__ == '__main__':
	try:
		app.run(main)
	except SystemExit:
		pass
