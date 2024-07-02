# %% Import necessary libraries 
from ultralytics import YOLO
from scipy.io import matlab
from Module.drawer import Drawer
from Module.calculation import *
import cv2
import time 
import numpy as np


# %% Initilize static variables
useNearest = False
scale = .5
start = time.time()
frame_cnt = 0

# %% Read all files
model = YOLO(r"Train/Pothole_Detector/Cook_Station_3/weights/best.pt", task = 'detect')
cap = cv2.VideoCapture(r"Resources/Video/Demo.mp4")
mat = matlab.loadmat(r"Resources/CameraIntrinsic.mat")

# %% Calculation of mapping from 2D to 3D (only works in out case, yours maybe different)
intrinsicMatrix = mat["IntrinsicMatrix"].T
ret, frame = cap.read()
frame = cv2.resize(frame, (int(frame.shape[1] * scale), int(frame.shape[0] * scale)))
xMapper, yMapper = SIApproxMapping(frame, 16 * np.pi / 180, 110, intrinsicMatrix)



# %% Main loop
while 1: 
    ret, frame = cap.read()
    
    # Check if the frame is read correctly
    if ret == False: 
        cv2.destroyAllWindows()
        cap.release()
        break
    
    confs = 15
    if confs == 0: confs = 1
    
   
    # Main core
    # STARTS HERE
    # Resize for better performance
    frame = cv2.resize(frame, (int(frame.shape[1] * scale), int(frame.shape[0] * scale)))
    origin = np.array([frame.shape[1] // 2, frame.shape[0] - 1])

    result = model.predict(frame, 
                           verbose = False, 
                           nms = True, 
                           half = True, 
                           iou = .65,
                           conf = confs / 100, 
                           device = 'cuda')[0]
    

    boxes = result.boxes
    masks = result.masks
    
    for idx, box in enumerate(boxes):
        if masks:
            # Retrieve the mask for the current index
            mask = masks[idx]
            # Convert mask coordinates to integer and adjust y-coordinates
            convertMask = np.int32(mask.xy[0]) 
            
            
            # Extract x and y coordinates from the mask
            x_coords = convertMask[:, 0]
            y_coords = convertMask[:, 1]
            
            x_coords = np.clip(x_coords, 0, frame.shape[1] - 1)
            y_coords = np.clip(y_coords, 0, frame.shape[0] - 1)

            # Convert to SI mapping
            maskSI = np.array([xMapper[y_coords, x_coords], yMapper[y_coords, x_coords]]).T
            originSI = np.array([xMapper[origin[1], origin[0]], yMapper[origin[1], origin[0]]])
                         
            if useNearest:
                nearIdx = nearestPoint(originSI, maskSI)
                Cx = x_coords[nearIdx]
                Cy = y_coords[nearIdx]
            else:
                center = centerOfMass(convertMask)
                Cx = center[0]
                Cy = center[1]
                
        
            targetPoint = np.array([Cx, Cy])
            
            length = round(np.sqrt(xMapper[Cy, Cx] ** 2 + yMapper[Cy, Cx] ** 2), 2)

            # Calculate bounding box coordinates in real-world scale
            # Lower case x, y means coordinates in array scale, upper case X, Y means coordinates in real-world scale
            xmax = x_coords.max()
            xmin = x_coords.min()
            ymax = y_coords.max()
            ymin = y_coords.min()
            
            Ymax, Ymin = yMapper[ymax, (xmax + xmin) // 2], yMapper[ymin, (xmin + xmax) // 2]
            Xmax, Xmin = xMapper[(ymax + ymin) // 2, xmax], xMapper[(ymin + ymax) // 2, xmin]
            
            drawer = Drawer(frame)
            
            # Draw bounding box and mask on the frame
            try:
                drawer.drawDist(origin, targetPoint, length)
                drawer.drawBox(box, (Ymin - Ymax, Xmax - Xmin))
                drawer.drawMask(convertMask)
            except:
                pass
        else:
            # Draw only the bounding box if no mask is available
            drawer.drawBox(box) 
    # ENDS HERE
       
    if time.time() - start >= 1:
        print(f"FPS: {frame_cnt}   ", end = '\r', flush = True)
        start = time.time()
        frame_cnt = 0
    frame_cnt += 1

    cv2.imshow("Image", frame)
    key = cv2.waitKey(1)


    if key == ord('k'):
        cv2.destroyAllWindows()
        cap.release()
        break

# %%