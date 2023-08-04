import fiftyone as fo
import fiftyone.zoo as foz

# A name for the dataset
name = "my-dataset"

# The directory containing the dataset to import
dataset_dir = "Autogathered_Dataset/1/"

# The type of the dataset being imported
dataset_type = fo.types.COCODetectionDataset  # for example

dataset = fo.Dataset.from_dir(
    dataset_dir=dataset_dir,
    dataset_type=dataset_type,
    name=name,
)
#dataset = foz.load_zoo_dataset("cifar10", split="test")

session = fo.launch_app(dataset, port=8000)
