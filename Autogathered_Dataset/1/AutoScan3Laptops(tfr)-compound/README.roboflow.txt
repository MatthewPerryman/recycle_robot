
Screws_detection - v11 AutoScan3Laptops
==============================

This dataset was exported via roboflow.ai on February 13, 2022 at 8:28 PM GMT

It includes 2002 images.
Screws are annotated in Tensorflow TFRecord (raccoon) format.

The following pre-processing was applied to each image:
* Resize to 416x416 (Stretch)

The following augmentation was applied to create 2 versions of each source image:
* 50% probability of horizontal flip
* Equal probability of one of the following 90-degree rotations: none, clockwise, counter-clockwise
* Random Gaussian blur of between 0 and 0.5 pixels

The following transformations were applied to the bounding boxes of each image:
* 50% probability of horizontal flip
* 50% probability of vertical flip


