# Importing Required Modules
import sys

import cv2
import requests
import numpy as np
import detect
from PIL import Image

# Exception Handling for invalid requests
try:
    # Creating an request object to store the response
    # The URL is referenced sys.argv[1]
    ImgRequest = requests.get("http://192.168.0.116:80/")
    # Verifying whether the specified URL exist or not
    if ImgRequest.status_code == requests.codes.ok:

        img = cv2.imdecode(np.asarray(bytearray(ImgRequest.content), dtype="uint8"), cv2.IMREAD_COLOR)

        detect()
        cv2.imshow("image", img)
        cv2.waitKey(0)
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
except Exception as e:
    print(str(e))
