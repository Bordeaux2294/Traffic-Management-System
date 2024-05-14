import cv2
import pandas as pd
from ultralytics import YOLO
import cvzone
import random
from datetime import datetime
import os
from moviepy.editor import ImageSequenceClip

def detect_accidents(video_path, class_list_path='coco1.txt'):
    model = YOLO('best.pt')

    cap = cv2.VideoCapture(video_path)

    my_file = open(class_list_path, "r")
    data = my_file.read()
    class_list = data.split("\n")

    count = 0
    accident_frames = []
    accident_detected = False

    while True:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        count += 1
        if count % 3 != 0:
            continue
        frame = cv2.resize(frame, (1020, 500))
        results = model.predict(frame, verbose=False)
        a = results[0].boxes.data
        px = pd.DataFrame(a).astype("float")

        for index, row in px.iterrows():
            x1 = int(row[0])
            y1 = int(row[1])
            x2 = int(row[2])
            y2 = int(row[3])
            d = int(row[5])
            c = class_list[d]

            if 'accident' in c:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 1)
                cvzone.putTextRect(frame, f'{c}', (x1, y1), 1, 1)
                accident_detected = True
            else:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 1)
                cvzone.putTextRect(frame, f'{c}', (x1, y1), 1, 1)

        if accident_detected:
            accident_frames.append(frame)
            if len(accident_frames) >= 15:  # 5 seconds (assuming 3 frames per second)
                break

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    violations_folder = "violations"
    if not os.path.exists(violations_folder):
        os.makedirs(violations_folder)

    # Get the current date and time
    now = datetime.now()
    date_time = now.strftime("%Y-%m-%d_%H-%M-%S")

    # Output video file path
    output_video_name = f'output_video_{date_time}.mp4'
    output_video_path = os.path.join(violations_folder, output_video_name)
    abs = os.path.abspath(output_video_path)
    # Write the frames to a video file
    clip = ImageSequenceClip(accident_frames, fps=25)
    clip.write_videofile(output_video_path, codec='libx264', ffmpeg_params=['-pix_fmt', 'yuv420p'])


    # Returning the required information
    places = ['Kingston','Portmore','St. James', 'St Elizabeth']
    random_index = random.randint(0, len(places) - 1)
    info=[]
    info_list = [output_video_name, "Crash",places[random_index], now, output_video_path]
    info.append(info_list)
    return info

