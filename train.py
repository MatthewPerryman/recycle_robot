import torch
from ultralytics import YOLO

def train():
    dataset = 'Autogathered_Dataset/2 (labeless removed)/dataset.yaml'
    output_path = 'Autogathered_Dataset/2 (labeless removed)/'
    output_dir = 'runs-50/'

    print(torch.cuda.device_count())

    model = YOLO('yolov8n.pt')

    # Train the model using the '2 (labeless removed)' dataset for 50 epochs
    results = model.train(data=dataset, epochs=50, device=0, batch=4, project=output_path, name=output_dir)

    # Evaluate the model's performance on the validation set
    results = model.val()

if __name__ == '__main__':
    train()