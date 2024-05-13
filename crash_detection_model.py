import cv2
import pandas as pd
from ultralytics import YOLO
import cvzone
import random
from datetime import datetime
import os

def detect_accidents(video_path, class_list_path='coco1.txt'):
    model = YOLO('yolov8n.pt')

    def RGB(event, x, y, flags, param):
        if event == cv2.EVENT_MOUSEMOVE:
            point = [x, y]
            print(point)

    cv2.namedWindow('RGB')
    cv2.setMouseCallback('RGB', RGB)

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
        results = model.predict(frame)
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

    # Save frames to a new video file with a timestamp in the filename
    if accident_frames:
        output_folder = "violations"
        os.makedirs(output_folder, exist_ok=True)  # Create the "violations" folder if it doesn't exist
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_video_name = f"accident_clip_{timestamp}.mp4"
        output_video_path = os.path.abspath(os.path.join(output_folder, output_video_name))  # Create an absolute file path inside the "violations" folder
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(output_video_path, fourcc, 3.0, (1020, 500))
        for frame in accident_frames:
            out.write(frame)
        out.release()

    cap.release()
    cv2.destroyAllWindows()

    # Returning the required information
    places = ['Kingston','Portmore','St. James', 'St Elizabeth']
    random_index = random.randint(0, len(places) - 1)
    info=[]
    info_list = [output_video_name, "Crash",places[random_index], datetime.now(), output_video_path]
    info.append(info_list)
    return info

