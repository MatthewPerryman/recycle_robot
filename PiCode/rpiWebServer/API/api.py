# This code is only run on rpi server
from json import JSONEncoder, loads, dumps
import numpy as np
from flask import Flask, request
from CamStream import ImageStream
from RobotArm import RobotController
from time import time
from ....Utils.Logging import write_log

app = Flask(__name__)


# The camera is focussed here, therefore set up lighting before starting the app
image_stream = ImageStream()
controller = RobotController.RobotController()

class NumpyArrayEncoder(JSONEncoder):
	def default(self, obj):
		if isinstance(obj, np.ndarray):
			return obj.tolist()
		return JSONEncoder.default(self, obj)


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
	json_coord = loads(request.data)
	Xd = json_coord['Xd']
	Yd = json_coord['Yd']
	Zd = json_coord['Zd']

	old, new = controller.move_by_vector((Xd, Yd, Zd))

	print("old: {}, new: {}".format(old, new))

	return "old: {}, new: {}".format(old, new)


# Compact command get information for screw localising
@app.route('/get_images_for_depth', methods=['GET'])
def get_images_for_depth():
	write_log("Reset Location: {}".format(time()))
	controller.swift.reset()

	write_log("Call image_stream get depth images")
	# Take a photo, move the camera 1 cm up, take another
	img1, f_len, img2 = image_stream.get_imgs_for_depth(controller.move_by_vector, write_log)

	write_log("Jsonify images")
	return_dict = {'img1': img1, 'f_len': f_len, 'img2': img2}
	encoded_dict_json = dumps(return_dict, cls=NumpyArrayEncoder)

	write_log("Send Images")
	# return json as dumps
	return encoded_dict_json


@app.route('/get_photo', methods=['GET'])
def live_photo():
	image = image_stream.take_photo()
	return image


if __name__ == '__main__':
	try:
		app.run(debug=True, port=80, host='0.0.0.0')
	except KeyboardInterrupt:
		image_stream.__del__
		controller.__del__
		exit()
