from ultralytics import YOLO
import matplotlib.pyplot as plt
import time
import cv2
import pafy
import numpy as np

model = YOLO('yolov8n.pt')

def density(frame):
    bounds = ((0,frame.shape[0]),(480,frame.shape[1]))
    y = bounds[0]
    x = bounds[1]
    frame = frame[y[0]:y[1], x[0]:x[1]]
    result = model(frame, verbose = False, classes=[2,3,5,7])
    area = ((y[1]-y[0])/200) * ((x[1]-x[0])/200)
    vehicles = len(result[0].boxes.cls)
    return vehicles/area
