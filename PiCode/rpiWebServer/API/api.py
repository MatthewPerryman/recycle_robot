from flask import Flask
from flask import send_from_directory
import cv2
from CamStream import ImageStream
import numpy as np
from RobotArm import RobotController
import json
from json import JSONEncoder

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
		
@app.route('/move_robot_to/<Xd>/<Yd>/<Zd>', methods=['POST'])
def move_robot_to(Xd, Yd, Zd):
	controller.move_to((Xd, Yd, Zd))
	
	return "Attempted"

# Compact command get information for screw localising
@app.route('/get_images_for_depth', methods=['GET'])
def get_images_for_depth():
	# Take a photo, move the camera 1 cm up, take another
	img1, f_len, img2 = image_stream.get_imgs_for_depth(controller.move_by_increment)
	
	return_dict = {'img1': img1, 'f_len': f_len, 'img2': img2}
	encoded_dict_json = json.dumps(return_dict, cls=NumpyArrayEncoder)
	
	# return json as dumps
	return encoded_dict_json

@app.route('/get_photo', methods=['GET'])
def live_photo():
	image = image_stream.take_photo()
	return image
	
if __name__ == '__main__':
	app.run(debug=True, port=80, host='0.0.0.0')
