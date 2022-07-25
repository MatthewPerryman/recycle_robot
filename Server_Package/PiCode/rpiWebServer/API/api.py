# This code is only run on rpi server
import json
from flask import Flask, request, send_file, jsonify
from Utils import Logging
from .CamStream import ImageStream
from .RobotArm import RobotController
import io
import numpy as np

app = Flask(__name__)

# The camera is focussed here, therefore set up lighting before starting the app
image_stream = ImageStream()
controller = RobotController.RobotController()


# API Control of Robot Arm
@app.route('/update_position', methods=['POST'])
def increment_position():
	update_vector = request.content
	if (update_vector > -10) and (update_vector < 10):
		controller.move_by_increment(update_vector)
		return "API Check Success"
	else:
		return "API Check Fail"


@app.route('/move_by_vector/', methods=['POST'])
def move_by_vector():
	json_coord = json.loads(request.data)
	Xd = json_coord['Xd']
	Yd = json_coord['Yd']
	Zd = json_coord['Zd']

	response = controller.move_by_vector((Xd, Yd, Zd))

	return jsonify(response=response)


# Method to reset robot location
@app.route('/reset_robot', methods=['POST'])
def reset_robot():
	controller.reset()


# Compact command get information for screw localising
@app.route('/get_images_for_depth', methods=['GET'])
def get_images_for_depth():
	Logging.write_log("server", "\nNew Run:\n")

	Logging.write_log("server", "Reset Location")
	controller.swift.reset()

	Logging.write_log("server", "Call image_stream get depth images")
	# Take a photo, move the camera 1 cm up, take another
	img1, f_len, img2 = image_stream.get_imgs_for_depth(controller.move_by_vector, Logging.write_log)

	Logging.write_log("server", "Compress Image")
	buffer = io.BytesIO()
	np.savez_compressed(buffer, img1, np.array([f_len]), img2)
	buffer.seek(0)

	Logging.write_log("server", "Send Images")
	print(buffer)
	return send_file(buffer, as_attachment=True, attachment_filename='depth_imgs.csv', mimetype="image/csv")


# Set robot position
@app.route('/set_position/', methods=['POST'])
def set_position():
	new_json = json.loads(request.data)
	new_location = [new_json['Xd'], new_json['Yd'], new_json['Zd']]

	response = controller.move_to(new_location)

	return jsonify(response=response)


# Retrieve robot position
@app.route('/get_position/', methods=['GET'])
def get_position():
	return "Position: {}".format(controller.swift.get_position())


@app.route('/get_photo', methods=['GET'])
def get_photo():
	image, f_len = image_stream.take_focused_photo()
	Logging.write_log("server", "Compress Image")

	print(image.shape)
	buffer = io.BytesIO()
	np.savez_compressed(buffer, image, np.array([f_len]))
	buffer.seek(0)

	Logging.write_log("server", "Send Image")
	return send_file(buffer, as_attachment=True, attachment_filename='singe_image.csv', mimetype="image/csv")


if __name__ == 'Server_Package.PiCode.rpiWebServer.API.api':
	try:
		app.run(port=1024, host='0.0.0.0')
	except KeyboardInterrupt:
		image_stream.__del__
		controller.__del__
		exit()
