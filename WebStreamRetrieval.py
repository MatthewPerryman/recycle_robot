# Importing Required Modules
import cv2
import requests
import numpy as np
from Model.detect import Classifier
from absl import app, logging
import time
import math
import json

# Note: all coordinates are x, y
image_shape = (640, 480, 3)
m_frame_distance = (0, 0, -10)

# Find the center pixel in the image
center_pixel = (image_shape[1] / 2, image_shape[0] / 2)

# Based upon datasheet https://cdn.sparkfun.com/datasheets/Dev/RaspberryPi/ov5647_full.pdf#:~:text=The%20OV5647%20is%20a%20low%20voltage%2C%20high%20performance%2C,the%20serial%20camera%20control%20bus%20or%20MIPI%20interface.
pixel_size = 0.0014  # (mm) = 1.4 micrometers

# (CMOS size - tot pixel size)/number of gaps (per axis)
pixel_gap_size_x = (5.52 - (pixel_size * 2592)) / 2591
pixel_gap_size_y = (4.7 - (pixel_size * 1944)) / 1943


# Find closest object to the center of the image
def find_closest_box(nums, img_boxes, scores):
    # Store the index and distance of the closest box to the center
    closest_to_center = [0, math.inf]
    for i in range(nums[0]):
        # Boxes: [[(x0, y0), (x3, y3)]]

        # Find the center coordinate
        center_coordinate = (img_boxes[i][0][0] + ((img_boxes[i][1][0] - img_boxes[i][0][0]) / 2),
                             img_boxes[i][0][1] + ((img_boxes[i][1][1] - img_boxes[i][0][1]) / 2))

        # Find the box center closest to the image center
        dist_to_center = math.hypot((center_coordinate[0] - center_pixel[0]),
                                    (center_coordinate[1] - center_pixel[1]))
        if dist_to_center < closest_to_center[1]:
            closest_to_center[0] = i
            closest_to_center[1] = dist_to_center
    # Outputs the box score and corner coordinates
    logging.info('\tClosest: Score: {}, Coords: {}'.format(np.array(scores[0][closest_to_center[0]]),
                                                           np.array(img_boxes[closest_to_center[0]])))
    # Return the closest box top left and right coordinates, and the hypot to centre
    return closest_to_center, center_coordinate, dist_to_center


def detect_screws_in_stream(model):
    while True:
        t1 = time.time()
        # Exception Handling for invalid requests
        try:
            c1 = time.time()
            # Creating an request object to store the response
            # The URL is referenced sys.argv[1]
            ImgRequest = requests.get("http://192.168.0.116:80/live_photo")
            # Verifying whether the specified URL exist or not
            if ImgRequest.status_code == requests.codes.ok:
                # Read numpy array bytes
                image = np.frombuffer(ImgRequest.content, dtype=np.uint8)

                # Reshape image values into 640 x 480 x 3 image as needed
                image = np.reshape(image, newshape=image_shape)
                c2 = time.time()
                t2 = time.time()

                # Display the labelled image with a delay of 1 millisecond (minimum delay)
                output_img, img_boxes, scores, nums = model.detect(image)

                if int(nums[0]) is not 0:
                    closest_box, _, _ = find_closest_box(nums, img_boxes, scores)

                cv2.imshow("Laptop", output_img)
                cv2.waitKey(1)
            else:
                print("Error: {}".format(ImgRequest.status_code))

            logging.info('Call API time: {}'.format(c2 - c1))
            logging.info('Full loop time: {}'.format(t2 - t1))
        except Exception as e:
            print(str(e))


def find_and_move_to_screw(model):
    try:
        # Creating an request object to store the response
        # The URL is referenced sys.argv[1]
        ImgRequest = requests.get("http://192.168.0.116:80/get_images_for_depth")
        if ImgRequest.status_code == requests.codes.ok:
            # Read numpy array bytes
            depth_dict = json.loads(ImgRequest.content)

            image1 = depth_dict['img1']
            f_len = depth_dict['f_len'] / 100
            image2 = depth_dict['img2']

            image1 = np.asarray(image1)
            image2 = np.asarray(image2)

            # Reshape image values into 640 x 480 x 3 image as needed
            image1 = np.reshape(image1, newshape=image_shape).astype(np.uint8)
            image2 = np.reshape(image2, newshape=image_shape).astype(np.uint8)

            # Locate and box the screws in both images
            output_img1, img_boxes1, scores1, nums1 = model.detect(image1)
            output_img2, img_boxes2, scores2, nums2 = model.detect(image2)

            if (int(nums1[0]) is not 0) and (int(nums2[0]) is not 0):
                # Check if this is a valid test scenario
                cv2.imshow("Img1", output_img1)
                cv2.waitKey(0)
                cv2.imshow("Img2", output_img2)
                cv2.waitKey(0)

                if input("Proceed?: ") == 'n':
                    cv2.destroyAllWindows()
                    return False

                # Given at least one screw is detected, find the center coordinate
                _, center_coord1, dist_to_center1 = find_closest_box(nums1, img_boxes1, scores1)
                _, center_coord2, dist_to_center2 = find_closest_box(nums2, img_boxes2, scores2)

                # Perpendicular Distance (d) from lens to laptop = distance moved (m (10mm)) / (1 - (Frame1Dist_to_Centre/Frame2Dist_to_Center
                d = 10 / (1 - (dist_to_center1 / dist_to_center2))

                # Distance from the camera in the z axis. Down is negative for these coordinates
                Zd = -d

                # Pixel x (Px) = (y axis distance between image center & box center * pixel size) + no. gaps between pixels * gap size
                # y axis label to match real world y and x
                pixel_diff = (center_pixel[0] - center_coord1[0], center_pixel[1] - center_coord1[1])
                Px = (pixel_diff[1] * pixel_size) + ((pixel_diff[1] - 1) * pixel_gap_size_y)
                # Pixel y (Py) same as above but with x axis distance
                Py = (pixel_diff[0] * pixel_size) + ((pixel_diff[0] - 1) * pixel_gap_size_x)

                # Ratio, divide x&y by focal length, multiply by real world distance
                Xd = (Zd * Px) / f_len
                Yd = (Zd * Py) / f_len

                json_coord = {'Xd': Xd, 'Yd': Yd, 'Zd': Zd}
                requests.post("http://192.168.0.116:80/move_robot_to/", data=json.dumps(json_coord))

                return True
            else:
                print("Error: No object was detected in one of the frames")

            # cv2.imshow("Img1", output_img1)
            # cv2.waitKey(0)
            # cv2.imshow("Img2", output_img2)
            # cv2.waitKey(0)

            cv2.destroyAllWindows()

            return False
        else:
            print("Error: {}".format(ImgRequest.status_code))
            return False
    except Exception as e:
        print(str(e))


def main(_argv):
    Model = Classifier()

    # detect_screws_in_stream(Model)
    while True:
        if find_and_move_to_screw(Model):
            break


if __name__ == '__main__':
    try:
        app.run(main)
    except SystemExit:
        pass
