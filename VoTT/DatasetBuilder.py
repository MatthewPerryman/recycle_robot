import os
import random
import json
import glob
import pandas as pd
import shutil


# Check the file is for the desired image & return relevant parameters
def to_csv(path, number):
	boxes = []
	with open(path) as f:
		data = json.load(f)
	# Check if file is for desired image (asset>name == desired image)
	if data["asset"]["name"] == "img" + str(number) + ".jpg":

		for box in data["regions"]:
			x_min = round(float(box["points"][0]["x"]))
			y_min = round(float(box["points"][0]["y"]))
			x_max = round(float(box["points"][2]["x"]))
			y_max = round(float(box["points"][2]["y"]))
			label = box["tags"][0]
			boxes.append((label, x_min, y_min, x_max, y_max))

		return (data["asset"]["name"],
				int(data["asset"]["size"]["width"]),
				int(data["asset"]["size"]["width"]),
				boxes)
	#   Move to dataset (train< 80%, else valid)
	# Extract CSV content


def main():
	# Randomise order of files (-3 for number of extra files in directory at present time)
	# If this needs to be adaptive, a for loop to check file names may be better
	column_name = ['filename', 'width', 'height', 'bounding_box']
	json_path = os.getcwd() + "/LabelledImages/"
	num_range = list(range(len(os.listdir(json_path)) - 3))
	train_size = round((51 / 100) * 80)

	random.shuffle(num_range)

	img_list = []

	# Extract files in a randomised order & place into train/ valid datasets
	for count, file_num in enumerate(num_range):
		for path in glob.glob(json_path + '/*.json'):
			parsed_content = to_csv(path, file_num)
			if parsed_content is not None:
				# Store box details
				img_list.append(parsed_content)

				# Move corresponding image to dataset location
				img_name = "img{}.jpg".format(file_num)
				img_path = "LabelledImages/vott-json-export/" + img_name
				if count < train_size - 1:
					img_target = "Dataset/Train/" + img_name
				else:
					img_target = "Dataset/Validation/" + img_name
				shutil.copy(img_path, img_target)

		# When all training and valid parameters are gathered, save the contents to files respectively.
		if count == train_size - 1:
			d_set = "train"
			files_df = pd.DataFrame(img_list, columns=column_name)

			file_name = "Dataset/{}_data.csv".format(d_set)
			files_df.to_csv(file_name, index=False)
			img_list = []

		elif count == num_range.__len__() - 1:
			d_set = "valid"
			files_df = pd.DataFrame(img_list, columns=column_name)
			file_name = "Dataset/{}_data.csv".format(d_set)
			files_df.to_csv(file_name, index=False)


main()
