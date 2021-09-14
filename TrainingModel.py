import pandas as pd
import os
import numpy as np

import tensorflow as tf
from tensorflow import keras
from yolov3_tf2.models import (
    YoloV3, yolo_anchors, yolo_anchor_masks)

TRAINING_CSV_FILE = 'Dataset/train_data.csv'
TRAINING_IMAGE_DIR = 'Dataset/Train/'

training_image_records = pd.read_csv(TRAINING_CSV_FILE)

train_image_path = os.path.join(os.getcwd(), TRAINING_IMAGE_DIR)

HEIGHT, WIDTH = 640, 640

train_images = []
train_targets = []
train_labels = []

# for index, row in training_image_records.iterrows():
#     (filename, width, height, boxes) = row
#
#     train_image_fullpath = os.path.join(train_image_path, filename)
#     train_img = keras.preprocessing.image.load_img(train_image_fullpath, target_size=(height, width))
#     train_img_arr = keras.preprocessing.image.img_to_array(train_img)
#
#     x_min = round(x_min / width, 2)
#     y_min = round(y_min / height, 2)
#     x_max = round(x_max / width, 2)
#     y_max = round(y_max / height, 2)
#
#     train_images.append(train_img_arr)
#     train_targets.append((x_min, y_min, x_max, y_max))
#     train_labels.append(class_name)

# print(train_labels)

# model = YoloV3(HEIGHT, training=True, classes=2)
# anchors = yolo_anchors
# anchor_masks = yolo_anchor_masks

y_train = tf.data.TextLineDataset("Datasets/train_data.csv")

print(y_train.element_spec)
