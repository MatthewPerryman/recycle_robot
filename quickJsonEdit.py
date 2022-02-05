import json

IMG_LABELS_FILE = "Autogathered_Dataset/img_labels.json"

with open(IMG_LABELS_FILE, "r") as labels_file:
	labels_data = json.load(labels_file)

for count, image in enumerate(labels_data['images']):
    image['license'] = 1


with open(IMG_LABELS_FILE, "w") as labels_file:
	json.dump(labels_data, labels_file)