# Importing Required Modules
import cv2
import requests
import numpy as np
from Model.detect import Classifier
from absl import app, logging
import time


image_shape = (640, 480, 3)


def main(_argv):
    Model = Classifier()
    while True:
        t1 = time.time()
        # Exception Handling for invalid requests
        try:
            c1 = time.time()
            # Creating an request object to store the response
            # The URL is referenced sys.argv[1]
            ImgRequest = requests.get("http://192.168.0.116:80/")
            # Verifying whether the specified URL exist or not
            if ImgRequest.status_code == requests.codes.ok:
                # Read numpy array bytes
                image = np.frombuffer(ImgRequest.content, dtype=np.uint8)

                # Reshape image values into 640 x 480 x 3 image as needed
                image = np.reshape(image, newshape=image_shape)
                c2 = time.time()
                t2 = time.time()

                # Dispay the labelled image with a delay of 1 millisecond (minimum delay)
                cv2.imshow("Laptop", Model.detect(image))
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
