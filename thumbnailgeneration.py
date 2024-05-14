import os
import cv2

def generate_thumbnail(video_path, thumbnail_path, frame_num=0):
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(thumbnail_path, frame)
    cap.release()

def generate_thumbnails_for_folder(folder_path, thumbnails_folder):
    if not os.path.exists(thumbnails_folder):
        os.makedirs(thumbnails_folder)
    video_files = [f for f in os.listdir(folder_path) if f.endswith((".mp4", ".avi", ".mkv"))]
    for video_file in video_files:
        video_path = os.path.join(folder_path, video_file)
        thumbnail_path = os.path.join(thumbnails_folder, os.path.splitext(video_file)[0] + ".jpeg")
        generate_thumbnail(video_path, thumbnail_path)

def generate_thumbnail_for_video(video_path, thumbnails_folder):
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    thumbnail_path = os.path.join(thumbnails_folder, video_name + ".jpeg")
    generate_thumbnail(video_path, thumbnail_path)
    return thumbnail_path