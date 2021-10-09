# Importing Required Modules
import cv2
import requests
import numpy as np
from Model.detect import Classifier
from absl import app, logging
import time
import math


image_shape = (640, 480, 3)

# Find the center pixel in the image
center_pixel = (image_shape[1]/2, image_shape[0]/2)


def main(_argv):
    Model = Classifier()
    while True:
        t1 = time.time()
        # Exception Handling for invalid requests
        try:
            c1 = time.time()
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
                output_img, img_boxes, scores, nums = Model.detect(image)

                # Find closest object to the center of the image
                if int(nums[0]) is not 0:
                    closest_to_center = [0, math.inf]
                    for i in range(nums[0]):
                        # Boxes: [[(x0, y0), (x3, y3)]]
                        # 0: top left
                        # 1: top right
                        # 2: bottom left
                        # 3: bottom right

                        # Create the coordinates
                        coordinates = np.empty((4, 2))
                        coordinates[0] = img_boxes[i][0][0], img_boxes[i][0][1]
                        coordinates[1] = img_boxes[i][1][0], img_boxes[i][0][1]
                        coordinates[2] = img_boxes[i][0][0], img_boxes[i][1][1]
                        coordinates[3] = img_boxes[i][1][0], img_boxes[i][1][1]

                        # Find closest corner to the image center
                        for j in range(coordinates.shape[0]):
                            dist_to_center = math.hypot((coordinates[j][0] - center_pixel[0]), (coordinates[j][1] - center_pixel[1]))
                            if dist_to_center < closest_to_center[1]:
                                closest_to_center[0] = i
                                closest_to_center[1] = dist_to_center
                    logging.info('\tClosest: Score: {}, Coords: {}'.format(np.array(scores[0][closest_to_center[0]]),
                                                                           np.array(img_boxes[closest_to_center[0]])))

                print("{}, {}".format(center_pixel[0], center_pixel[1]))
                cv2.imshow("Laptop", output_img)
                cv2.waitKey(1)
            else:
                print("Error: {}".format(ImgRequest.status_code))

            logging.info('Call API time: {}'.format(c2 - c1))
            logging.info('Full loop time: {}'.format(t2 - t1))
        except Exception as e:
            print(str(e))


if __name__ == '__main__':
    try:
        app.run(main)
    except SystemExit:
        pass
