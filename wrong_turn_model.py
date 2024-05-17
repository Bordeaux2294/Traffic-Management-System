from datetime import datetime
import os
import cvzone
import cv2
import numpy as np
from ultralytics import YOLO
from collections import defaultdict
import random

model = YOLO('yolov8n.pt')

def detect_wrong_turn(video_path):

    cap = cv2.VideoCapture(video_path)
    output_video_path = 'wrong_turn1.mp4'

    fgbg = cv2.createBackgroundSubtractorMOG2()
    area1=[(71, 212),(329, 247),(324, 270),(31, 236)]
    area2=[(280, 240),(322, 141),(357, 146),(319, 251)]

    vid={}
    counter=[]
    count = 0
    track_history = defaultdict(lambda: [])

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')  # Define the codec
    out = cv2.VideoWriter(f"violations\\"+output_video_path, fourcc, fps, (frame_width, frame_height))

    #create a folder with the current date and time as the folder name
    def save_frame(frame):
        current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
        folder_name = f"violations"
        os.makedirs(folder_name, exist_ok=True)
        image = os.path.join(folder_name, f"wrong_turn_{current_datetime}.jpg")
        cv2.imwrite(image, frame)

    while cap.isOpened():
        success, frame = cap.read()
        track_ids = []

        if not success:
            break
        #frame=cv2.resize(frame,(1020,500))
        frame=cv2.resize(frame,(450,360))

        # Apply background subtraction
        #fgbg represents clear bg, subtracting the background
        fgmask = fgbg.apply(frame)

        #threshold the foreground mask
        _, thresh = cv2.threshold(fgmask, 250, 255, cv2.THRESH_BINARY)

        # Find contours in the thresholded image
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        #store vehicle coordinates and ids
        list=[]
        for contour in contours:
            if cv2.contourArea(contour) >= 7:  # Adjust the area threshold as needed
                x, y, w, h = cv2.boundingRect(contour)
                i = 1
                list.append([x,y,w,h,1])
        results = model.track(frame, classes=[2], persist=True, verbose = False)
        if results[0].boxes.id != None:
            boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
            track_ids = results[0].boxes.id.cpu().numpy().astype(int)
            confidences = results[0].boxes.conf.cpu().numpy().astype(int)

        annotated_frame = results[0].plot()
        frame = annotated_frame

        for box, track_id in zip(results[0].boxes.xyxy.cpu().numpy().astype(int), track_ids):
            x, y, w, h = box
            track = track_history[track_id]
            track.append((float(x), float(y)))  # x, y center point
            if len(track) > 30:  # retain 90 tracks for 90 frames
                track.pop(0)

        bbox_idx=list
        for bbox in bbox_idx:

            x1,y1,w1,h1,id=bbox

            cx=int(x1+x1+w1)//2
            cy=int(y1+y1+h1)//2
            result=cv2.pointPolygonTest(np.array(area1,np.int32),((cx,cy)),False)
            if result>=0:
                vid[id]=(cx,cy)
            if id in vid:
                result1=cv2.pointPolygonTest(np.array(area2,np.int32),((cx,cy)),False)
                if result1>=0:

                    if counter.count(id)==0:
                        counter.append(id)
                        save_frame(frame)


        cv2.polylines(frame,[np.array(area1,np.int32)],True,(0,255,0),2)
        cv2.polylines(frame,[np.array(area2,np.int32)],True,(0,0,255),2)


        p=len(counter)
        #add text with counter to screen
        cvzone.putTextRect(frame,f'Wrong turns: {p}',(10,50),1,2,
            colorT=(255,255, 255), colorR=(1, 1, 1),
            font=cv2.FONT_HERSHEY_SIMPLEX,
            offset=10,
            border=1, colorB=(255, 255, 255))
        out.write(frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break


    cap.release()
    cv2.destroyAllWindows()
    out.release()

    info=[]
    places = ['Kingston','Portmore','St. James', 'St Elizabeth']
    random_index = random.randint(0, len(places) - 1)
    output_video = os.path.abspath(os.path.join("violations", "wrong_turn1.mp4"))

    info_list = [output_video_path, "Illegal Turn", places[random_index], datetime.now(), output_video]
    info.append(info_list)
    return info

