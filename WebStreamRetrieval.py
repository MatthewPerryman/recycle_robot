# Importing Required Modules
import requests
import numpy as np
from Model.detect import detect
from absl import app
import io
from PIL import Image


def main(_argv):
    # Exception Handling for invalid requests
    try:
        # Creating an request object to store the response
        # The URL is referenced sys.argv[1]
        ImgRequest = requests.get("http://192.168.0.116:80/")
        # Verifying whether the specified URL exist or not
        if ImgRequest.status_code == requests.codes.ok:
            image = np.array(Image.open(io.BytesIO(ImgRequest.content)))
            #img = np.asarray(bytearray(ImgRequest.content), dtype="uint8")

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
    except Exception as e:
        print(str(e))


if __name__ == '__main__':
    try:
        app.run(main)
    except SystemExit:
        pass
