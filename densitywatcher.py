from ultralytics import YOLO
import matplotlib.pyplot as plt
import time
import cv2
import pafy
import numpy as np


model = YOLO('yolov8n.pt')
box = []

# YouTube video URL or ID
video_url = 'https://www.youtube.com/watch?v=7I8uU730tTs'

# Load the video using pafy
video = pafy.new(video_url)
best = video.getbest(preftype="mp4")
capture = cv2.VideoCapture(best.url)
fps = int(capture.get(cv2.CAP_PROP_FPS))
count = 0
while True:
    ret, frame = capture.read()
    if not ret:
        break

    # Perform object detection on the frame using Ultralytics YOLO
    # Replace the following line with your YOLO inference code
    if count%(fps*2) == 0:
       result = model(frame,classes=[2,3,5,7], verbose=False)
       print(count)
       den = len(result[0].boxes.cls)/10
       box.append(den)
       if len(box) >= 5:
          print(np.mean(box))
          box = box[1:]
    # Display the frame with object detection results
       cv2.imshow('YOLO Object Detection', frame)
       cv2.imwrite(f'saved_frame{count}.jpg', result[0].plot())
       count += 1
       if cv2.waitKey(1) & 0xFF == ord('q'):
           break
    elif count < 500:
         count += 1
    else:
         break
    

capture.release()
cv2.destroyAllWindows()
