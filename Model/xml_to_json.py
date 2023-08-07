# Import libraries
import os
import json
import xml.etree.ElementTree as ET

# Define the folder path of the xml files
xml_folder = 'C:/Users/drago/Documents/gitrepos/Cross-Recessed-Screw_Deep-Learning-Datasets/'
xml_training_data = xml_folder + 'Training_Images/'

xml_training_annots = xml_folder + 'Training_Annotations/'

# Define the output file name of the coco json file
coco_file = xml_training_annots + "coco.json"

# Define the coco dictionary keys
coco_keys = ["file_name", "licenses", "images", "annotations", "categories"]

# Initialize the coco dictionary
coco_dict = {}
for key in coco_keys:
    coco_dict[key] = []

# Loop through the xml files in the folder
for xml_file in os.listdir(xml_training_annots):
    if os.path.join(xml_training_annots, xml_file).endswith(".xml") == False:
        continue

    # Parse the xml file
    tree = ET.parse(os.path.join(xml_training_annots, xml_file))
    root = tree.getroot()

    # Get the image id, file name, width and height from the xml file
    image_id = int(root.find("filename").text.split(".")[0])
    file_name = xml_training_data + root.find("filename").text
    width = int(root.find("size/width").text)
    height = int(root.find("size/height").text)
    depth = int(root.find("size/depth").text)

    # Append the image information to the coco dictionary
    coco_dict["images"].append({
        "id": image_id,
        "file_name": file_name,
        "width": width,
        "height": height,
        "depth": depth
    })

    # Loop through the objects in the xml file
    for obj in root.findall("object"):
        # Get the category id, name, bounding box coordinates and segmentation points from the xml file
        category_id = 2 if obj.find("name").text == 'cross_recessed_screw' else 0
        category_name = obj.find("name").text
        xmin = int(obj.find("bndbox/xmin").text)
        ymin = int(obj.find("bndbox/ymin").text)
        xmax = int(obj.find("bndbox/xmax").text)
        ymax = int(obj.find("bndbox/ymax").text)

        # Calculate the area and width and height of the bounding box
        area = (xmax - xmin) * (ymax - ymin)
        bbox_width = xmax - xmin
        bbox_height = ymax - ymin

        # Append the annotation information to the coco dictionary
        coco_dict["annotations"].append({
            "id": len(coco_dict["annotations"]) + 1,
            "image_id": image_id,
            "category_id": category_id,
            "area": area,
            "bbox": [xmin, ymin, bbox_width, bbox_height]
        })

        # Append the category information to the coco dictionary if not already present
        if category_id not in [cat["id"] for cat in coco_dict["categories"]]:
            coco_dict["categories"].append({
                "id": category_id,
                "name": category_name,
                "supercategory": category_name
            })

# Write the coco dictionary to the output file as json format
with open(coco_file, "w") as f:
    json.dump(coco_dict, f, indent=4)

print(f"Successfully converted {len(os.listdir(xml_training_annots))} xml files to {coco_file}")
