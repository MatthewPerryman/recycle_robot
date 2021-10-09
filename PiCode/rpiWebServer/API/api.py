from flask import Flask
from flask import send_from_directory
import cv2
from CamStream import ImageStream
import numpy as np
from RobotArm import RobotController

app = Flask(__name__)
# The camera is focussed here, therefore set up lighting before starting the app
image_stream = ImageStream()
controller = RobotController.RobotController()

@app.route('/update_position', methods=['PUT'])
def increment_position():
	update_vector = request.content
	if (update_vector > -10) and (update_vector < 10):
		controller.move_by_increment(update_vector)
		return "API Check Success"
	else:
		return "API Check Fail"

@app.route('/get_photo', methods=['GET'])
def live_photo():
	image_stream.cam_open()
	image = image_stream.take_photo()
	return image.tobytes()
	
if __name__ == '__main__':
	app.run(debug=True, port=80, host='0.0.0.0')
