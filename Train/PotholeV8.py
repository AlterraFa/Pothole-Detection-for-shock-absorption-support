#!/usr/bin/env python3
from ultralytics import YOLO
import argparse
import sys
import ast 

def parse_list(arg):
    try:
        return ast.literal_eval(arg)
    except ValueError:
        raise argparse.ArgumentTypeError("Argument must be a list of integers.")

parser = argparse.ArgumentParser()
parser.add_argument('-directory', type=str, help='Directory to model for training')
parser.add_argument('-project', type=str, help='Parent folder name')
parser.add_argument('-name', type=str, help="Name of checkpoint")
parser.add_argument('-batch', type=int, help="Number of simultaneous training images")
parser.add_argument('-epoch', type=int, help="Number of epochs")
parser.add_argument('-freeze', type=parse_list, help="Freezing range")
args = parser.parse_args()

global num_freeze
num_freeze = args.freeze

def freeze_layer(trainer):
    model = trainer.model
    print(f"Freezing {num_freeze[1] - num_freeze[0]} layers")
    freeze = [f'model.{x}.' for x in range(*num_freeze)]  # layers to freeze 
    for k, v in model.named_parameters(): 
        v.requires_grad = True  # train all layers 
        if any(x in k for x in freeze): 
            print(f'freezing {k}') 
            v.requires_grad = False 
    print(f"{num_freeze[1] - num_freeze[0]} layers are freezed.")

model = YOLO(model = args.directory, task = 'segment')
model.add_callback("on_train_start", freeze_layer)

try:
    model.train(
        data = r"/mnt/6208995F089932D1/Coding/Python/Final_Project/Resources/PotholeDataset/data.yaml", # Path to the dataset configuration file (e.g., coco8.yaml). This file contains dataset-specific parameters, including paths to training and validation data, class names, and number of classes.
        task = 'segment', # Specifies the task type, either 'segment' for segmentation or 'detect' for object detection.
        epochs = args.epoch, # Number of training epochs.
        imgsz = 640, # Target image size for training. All images are resized to this dimension before being fed into the model. Affects model accuracy and computational complexity.
       
        
        batch = args.batch, 
        patience = 20, # Number of epochs to wait without improvement in validation metrics before early stopping the training. Helps prevent overfitting by stopping training when performance plateaus.
        verbose = True, # Whether to display verbose output during training.
        dropout = 0.35, # Dropout rate for the model.
        optimizer = 'auto', #  	Choice of optimizer for training. Options include SGD, Adam, AdamW, NAdam, RAdam, RMSProp etc., or auto for automatic selection based on model configuration. Affects convergence speed and stability.
        cos_lr = True, # Whether to use cosine learning rate scheduling or not.
        label_smoothing = 0.15, # Applies label smoothing, softening hard labels to a mix of the target label and a uniform distribution over labels, can improve generalization.
         
        
        cls = 0.75, # Weight of the classification loss in the total loss function, affecting the importance of correct class prediction relative to other components.
        box = 12.5, # Weight of the box loss component in the loss function, influencing how much emphasis is placed on accurately predicting bounding box coordinates.
        

        overlap_mask = True, # Whether to use overlap mask for segmentation or not.
        nms = True, # Adds Non-Maximum Suppression (NMS) to the CoreML export, essential for accurate and efficient detection post-processing.
        iou = .65, # Intersection over Union (IoU) threshold for NMS, determining how similar boxes need to be to be considered for suppression.
        conf = .12, # Confidence threshold for NMS, determining the minimum confidence level for a box to be considered for suppression.
        
       
        device = [0], # Specifies the computational device(s) for training: a single GPU (device=0), multiple GPUs (device=0,1), CPU (device=cpu), or MPS for Apple silicon (device=mps).
        workers = 12,  # Number of worker threads for data loading (per RANK if Multi-GPU training). Influences the speed of data preprocessing and feeding into the model, especially useful in multi-GPU setups.
        cache = 'ram', # Cache mode for data loading, either 'disk' or 'memory'. 'disk' stores cached data on disk, while 'memory' stores it in memory.
 
 
        plots = True, # Generates and saves plots of training and validation metrics, as well as prediction examples, providing visual insights into model performance and learning progression.
        show = True, # Displays images during training, useful for debugging and visualizing data augmentation effects.
        visualize = True, # Visualizes model predictions during training, providing visual insights into model performance and learning progression.
        save = True, # Saves model checkpoints and training logs to disk.
        save_txt = True,
        show_boxes = True, # Whether to display bounding boxes during training.
        
        
        project = f"{args.project}", # Name of the project directory where training outputs are saved. Allows for organized storage of different experiments.
        name = args.name, # Name of the model checkpoint file.
        seed = 0, # Seed for random number generation, ensuring reproducibility in training.
        exist_ok = True, # If True, allows overwriting of an existing project/name directory. Useful for iterative experimentation without needing to manually clear previous outputs.
        
    )
     
except RuntimeError as e:
    print(f"An error occurred: {e}", file=sys.stderr)
    sys.exit(1)
sys.exit(0)