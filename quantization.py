from ultralytics import YOLO

model = YOLO("./Train/Pothole_Detector/Cook_Station_3/weights/best.pt")

model.export(format = "tensorrt", imgsz = 640, half = True)