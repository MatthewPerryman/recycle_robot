import time

import cv2
import numpy as np
import tensorflow as tf
from absl import flags, logging
from absl.flags import FLAGS

from Model.yolov3_tf2.dataset import load_tfrecord_dataset, transform_images
from Model.yolov3_tf2.models import YoloV3, YoloV3Tiny
from Model.yolov3_tf2.utils import draw_outputs

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
		img_raw = np.ndarray
		# Check an image was passed in
		if _argv is not None:
			img_raw = _argv
			if type(img_raw) is not np.ndarray or img_raw.shape != (FLAGS.size, FLAGS.size):
				raise ValueError("The input image array must be of type np.ndarray of shape ({}, {})".format(FLAGS.size, FLAGS.size))
		else:
			raise ValueError("Error: No image Inputted")

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
		img = cv2.cvtColor(img_raw, cv2.COLOR_RGB2BGR)
		img, img_adjusted_coords = draw_outputs(img, (boxes, scores, classes, nums), self.class_names)

		# Display location of each detected screw
		logging.info('Image Adjusted Detections:')
		for i in range(nums[0]):
			logging.info('\t{}, {}, {}'.format(self.class_names[int(classes[0][i])],
											   np.array(scores[0][i]),
											   np.array(img_adjusted_coords[i])))
		return img, img_adjusted_coords, scores, nums
