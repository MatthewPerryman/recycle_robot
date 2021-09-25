from flask import Flask
from flask import send_from_directory
import cv2
from CamStream import ImageStream
import numpy as np

app = Flask(__name__)
image_stream = ImageStream()

@app.route('/', methods=['GET'])
def live_photo():
	image_stream.cam_open()
	image = image_stream.take_photo()
	return image.tobytes()
	
if __name__ == '__main__':
	app.run(debug=True, port=80, host='0.0.0.0')
