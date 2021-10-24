import time
from absl import flags, logging
from absl.flags import FLAGS
import cv2
import numpy as np
import tensorflow as tf
from Model.yolov3_tf2_detection_requirements.models import (
	YoloV3, YoloV3Tiny
)
from Model.yolov3_tf2_detection_requirements.dataset import transform_images, load_tfrecord_dataset
from Model.yolov3_tf2_detection_requirements.utils import draw_outputs

flags.DEFINE_string('classes', "./Model/JustLaptopData/screws.names", 'path to classes file')
flags.DEFINE_string('weights', './Model/checkpoint/yolov3_train_82.tf', 'path to weights file')
flags.DEFINE_boolean('tiny', True, 'yolov3 or yolov3-tiny')
flags.DEFINE_integer('size', 416, 'resize images to')
flags.DEFINE_string('image', './data/meme.jpg', 'path to input image')
flags.DEFINE_string('tfrecord', './Model/JustLaptopData/test/Screws.tfrecord', 'tfrecord instead of image')
flags.DEFINE_string('output', './output.jpg', 'path to output image')
flags.DEFINE_integer('num_classes', 1, 'number of classes in the model')


class Classifier:
	physical_devices = tf.config.experimental.list_physical_devices('GPU')

	def __init__(self):
		for physical_device in self.physical_devices:
			tf.config.experimental.set_memory_growth(physical_device, True)

		if FLAGS.tiny:
			self.yolo = YoloV3Tiny(classes=FLAGS.num_classes)
		else:
			self.yolo = YoloV3(classes=FLAGS.num_classes)

		self.yolo.load_weights(FLAGS.weights).expect_partial()
		logging.info('weights loaded')

		self.class_names = [c.strip() for c in open(FLAGS.classes).readlines()]
		logging.info('classes loaded')

	def detect(self, _argv=None):
		# Check an image was passed in
		if _argv is not None:
			img_raw = _argv
		else:
			logging.info("Error: No image Inputted")

		img = tf.expand_dims(img_raw, 0)
		img = transform_images(img, FLAGS.size)

		# Find the screws in the image and get time
		t1 = time.time()
		boxes, scores, classes, nums = self.yolo(img)
		t2 = time.time()
		logging.info('Detection time: {}'.format(t2 - t1))

		# # Display location of each detected screw
		# logging.info('detections:')
		# for i in range(nums[0]):
		#     logging.info('\t{}, {}, {}'.format(self.class_names[int(classes[0][i])],
		#                                        np.array(scores[0][i]),
		#                                        np.array(boxes[0][i])))

		# Highlight the screws within the image
		if _argv is None:
			img = cv2.cvtColor(img_raw.numpy(), cv2.COLOR_RGB2BGR)
		else:
			img = cv2.cvtColor(img_raw, cv2.COLOR_RGB2BGR)
		img, img_adjusted_coords = draw_outputs(img, (boxes, scores, classes, nums), self.class_names)

		# Display location of each detected screw
		logging.info('Image Adjusted Detections:')
		for i in range(nums[0]):
			logging.info('\t{}, {}, {}'.format(self.class_names[int(classes[0][i])],
											   np.array(scores[0][i]),
											   np.array(img_adjusted_coords[i])))
		return img, img_adjusted_coords, scores, nums
