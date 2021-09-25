# Importing Required Modules
import requests
import numpy as np
from Model.detect import detect
from absl import app, logging
import time

image_shape = (640, 480, 3)

def main(_argv):
    t1 = time.time()
    # Exception Handling for invalid requests
    try:
        # Creating an request object to store the response
        # The URL is referenced sys.argv[1]
        ImgRequest = requests.get("http://192.168.0.116:80/")
        # Verifying whether the specified URL exist or not
        if ImgRequest.status_code == requests.codes.ok:
            # Read numpy array bytes
            image = np.frombuffer(ImgRequest.content, dtype=np.uint8)
            # Reshape image values into 640 x 480 x 3 image as needed
            image = np.reshape(image, newshape=image_shape)
            detect(image)

            # Opening a file to write bytes from response content
            # Storing this object as an image file on the hard drive
            # img = open("test.jpg", "wb")
            # img.write(ImgRequest.content)
            # img.close()
            # Opening Image file using PIL Image
            # img = Image.open("test.jpg")
            # img.show()
        else:
            print(ImgRequest.status_code)
        t2 = time.time()
        logging.info('time: {}'.format(t2 - t1))
    except Exception as e:
        print(str(e))


if __name__ == '__main__':
    try:
        app.run(main)
    except SystemExit:
        pass
