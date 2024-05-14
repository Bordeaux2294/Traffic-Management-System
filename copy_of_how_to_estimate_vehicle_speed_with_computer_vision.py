from moviepy.editor import ImageSequenceClip
import cv2
import pandas as pd
from ultralytics import YOLO
from tracker import *
import time
import datetime
import os

def process_video():
    model = YOLO('yolov8s.pt')

    class_list = ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush']

    tracker = Tracker()
    count = 0
    down = {}
    up = {}
    counter_down = []
    counter_up = []

    cap = cv2.VideoCapture('highway_mini.mp4')

    # Create a folder named "violations" if it doesn't exist
    folder_name = "violations"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    frames = []  # List to store frames

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        count += 1
        frame = cv2.resize(frame, (1020, 500))

        results = model.predict(frame)
        a = results[0].boxes.data
        a = a.detach().cpu().numpy()
        px = pd.DataFrame(a).astype("float")

        list = []

        for index, row in px.iterrows():
            x1 = int(row[0])
            y1 = int(row[1])
            x2 = int(row[2])
            y2 = int(row[3])
            d = int(row[5])
            c = class_list[d]
            # Removing the condition that filters out only cars
            list.append([x1, y1, x2, y2])

        bbox_id = tracker.update(list)

        for bbox in bbox_id:
            x3, y3, x4, y4, id = bbox
            cx = int(x3 + x4) // 2
            cy = int(y3 + y4) // 2
            red_line_y = 198
            blue_line_y = 268
            offset = 7

            if blue_line_y < (cy + offset) and blue_line_y > (cy - offset):
                up[id] = time.time()
            if id in up:
                if red_line_y < (cy + offset) and red_line_y > (cy - offset):
                    elapsed1_time = time.time() - up[id]
                    if counter_up.count(id) == 0:
                        counter_up.append(id)
                        distance1 = 10
                        a_speed_ms1 = distance1 / elapsed1_time
                        a_speed_kh1 = a_speed_ms1 * 3.6
                        if a_speed_kh1 > 100:  # Check if speed exceeds 100 km/hr
                            cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
                            cv2.rectangle(frame, (x3, y3), (x4, y4), (0, 255, 0), 2)
                            cv2.putText(frame, str(id), (x3, y3), cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255), 1)
                            cv2.putText(frame, str(int(a_speed_kh1)) + 'Km/h', (x4, y4), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 2)

            if red_line_y < (cy + offset) and red_line_y > (cy - offset):
                down[id] = time.time()
            if id in down:
                if blue_line_y < (cy + offset) and blue_line_y > (cy - offset):
                    elapsed_time = time.time() - down[id]
                    if counter_down.count(id) == 0:
                        counter_down.append(id)
                        distance = 10
                        a_speed_ms = distance / elapsed_time
                        a_speed_kh = a_speed_ms * 36
                        if a_speed_kh > 60:  # Check if speed exceeds 60 km/hr
                            cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
                            cv2.rectangle(frame, (x3, y3), (x4, y4), (0, 255, 0), 2)
                            cv2.putText(frame, str(id), (x3, y3), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                            cv2.putText(frame, str(int(a_speed_kh)) + 'Km/h', (x4, y4), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 255), 2)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
        frames.append(frame_rgb)  # Append the processed frame to the list

    # Release video capture
    cap.release()

    # Write the annotated frames to a video using MoviePy
    output_video_name = os.path.join(folder_name, 'annotated_video_{}.mp4'.format(datetime.datetime.now().strftime("%Y%m%d%H%M%S")))
    clip = ImageSequenceClip(frames, fps=30)
    clip.write_videofile(output_video_name, codec='libx264', ffmpeg_params=['-pix_fmt', 'yuv420p'])

    cv2.destroyAllWindows()

    # Return the required information
    video_name = 'highway_mini.mp4'
    keyword = 'speed'
    location = 'Kingston'
    now = datetime.datetime.now()
    creation_date = now.strftime("%Y-%m-%d %H:%M:%S")
    output_video_path = os.path.abspath(output_video_name)

    return [video_name, keyword, location, creation_date, output_video_path]

process_video()
