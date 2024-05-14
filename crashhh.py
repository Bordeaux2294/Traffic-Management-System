from moviepy.editor import ImageSequenceClip
import cv2
import pandas as pd
from ultralytics import YOLO
import cvzone
import time
from datetime import datetime
import os

def detect_accidents(video_path, model_path='best.pt', class_list_path='coco1.txt'):
    model = YOLO(model_path)

    cap = cv2.VideoCapture(video_path)

    my_file = open(class_list_path, "r")
    data = my_file.read()
    class_list = data.split("\n")

    count = 0
    accident_frames = []
    before_accident_frames = []
    after_accident_frames = []
    accident_detected = False
    duration_before = 0  # Initialize duration before accident
    duration_after = 0   # Initialize duration after accident

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
            duration_after += 1  # Increment the duration after accident

            if duration_before < 4 * 25:  # 4 seconds at 25 fps
                before_accident_frames.append(frame)
                duration_before += 1  # Increment the duration before accident
            elif duration_after >= 3 * 25:  # 3 seconds at 25 fps
                break

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

    # Create a folder called "violations" if it doesn't exist
    violations_folder = "violations"
    if not os.path.exists(violations_folder):
        os.makedirs(violations_folder)

    # Get the current date and time
    now = datetime.now()
    date_time = now.strftime("%Y-%m-%d_%H-%M-%S")

    # Output video file path
    output_video_path = os.path.join(violations_folder, f'output_video_{date_time}.mp4')

    # Concatenate frames before and after accident
    final_frames = before_accident_frames + accident_frames + after_accident_frames

    # Convert frames to RGB and append to the list
    frames = []
    for frame in final_frames:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frames.append(frame_rgb)

    # Write the clip to a video file
    clip = ImageSequenceClip(frames, fps=25)
    clip.write_videofile(output_video_path, codec='libx264', ffmpeg_params=['-pix_fmt', 'yuv444p'])

    # Return information about the output video
    return [
        f'output_video_{date_time}.mp4',  # video_name
        'crash',                           # word
        'Kingston',                        # location
        date_time,                         # date_time
        os.path.abspath(output_video_path) # absolute_file_path
    ]

# Example usage
output_info = detect_accidents('cr4.mp4')
print(output_info)

