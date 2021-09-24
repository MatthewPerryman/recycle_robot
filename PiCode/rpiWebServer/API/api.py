from flask import Flask
from flask import send_from_directory
import cv2

app = Flask(__name__)

@app.route('/', methods=['GET'])
def image():
	return send_from_directory('', 'img26.jpg')
	
if __name__ == '__main__':
	app.run(debug=True, port=80, host='0.0.0.0')
