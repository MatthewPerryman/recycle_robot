from flask import Flask
from flask import send_from_directory
import cv2
from CamStream import ImageStream
import numpy as np
from RobotArm import RobotController
import json

app = Flask(__name__)
# The camera is focussed here, therefore set up lighting before starting the app
image_stream = ImageStream()
controller = RobotController.RobotController()

# API Control of Robot Arm
@app.route('/update_position', methods=['PUT'])
def increment_position():
	update_vector = request.content
	if (update_vector > -10) and (update_vector < 10):
		controller.move_by_increment(update_vector)
		return "API Check Success"
	else:
		return "API Check Fail"
		
@app.route('/move_robot_to', methods=['PUT'])
def move_robot_to():
	relative_vector = request.content
	controller.move_to(relative_vector)

# Compact command get information for screw localising
@app.route('/get_images_for_depth', methods=['PUT']
def get_images_for_depth():
	# Take a photo, move the camera 1 cm up, take another
	img1, f_len, img2 = image_stream.get_imgs_for_depth(controller.move_by_increment)
	
	return_dict = {'img1': img1, 'f_len': f_len, 'img2': img2}
	# return json as dump
	return json.dump(json.loads(return_dict))

@app.route('/get_photo', methods=['GET'])
def live_photo():
	image = image_stream.take_photo()
	return image
	
if __name__ == '__main__':
	app.run(debug=True, port=80, host='0.0.0.0')
