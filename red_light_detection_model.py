from ultralytics import YOLO
import cv2
import numpy as np
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from datetime import datetime
import os

def RLV_Model(video_source,place):
    model = YOLO('yolov8n.pt')

    def crop_image(image, boundaries):
        cropped_images = []
        for boundary in boundaries:
            x, y, w, h = map(int, boundary)
            cropped_images.append(image[y:h, x:w])
        return cropped_images

    def is_red_light(image_path):
        hsv_img = cv2.cvtColor(image_path, cv2.COLOR_BGR2HSV)

        # Define the range of red color in HSV
        lower_red = np.array([0, 50, 50])
        upper_red = np.array([10, 255, 255])
        mask1 = cv2.inRange(hsv_img, lower_red, upper_red)

        lower_red = np.array([170, 50, 50])
        upper_red = np.array([180, 255, 255])
        mask2 = cv2.inRange(hsv_img, lower_red, upper_red)

        mask = cv2.bitwise_or(mask1, mask2)
        res = cv2.bitwise_and(image_path, image_path, mask=mask)
        red_pixel_count = cv2.countNonZero(mask)
        red_threshold = 60

        if red_pixel_count > red_threshold:
            return True
        else:
            return False


    def check_violation(vehicles,frame, frame_counter):
        def check_intersection(bbox, line_of_interest):
            x, y, w, h = map(int, bbox)
            if h >= line_of_interest-2 and h<= line_of_interest +2:
                return True
            else:
                return False

        # Loop through each detected vehicle
        violations=False
        for i, vehicle in enumerate(vehicles):
            violation = check_intersection(vehicle, line_of_interest)

            if violation:
                # print("ran red light")
                # cv2_imshow(crop_image(frame, vehicles)[i])
                # cv2.waitKey(0)
                # cv2.destroyAllWindows()
                capture_video_snippet(video_source, frame_counter)
                violations = True
        return violations


    def capture_video_snippet(video_path, violation_frame_num, snippet_duration=120):
        cap = cv2.VideoCapture(video_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        start_frame = max(0, violation_frame_num - snippet_duration)
        end_frame = min(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), violation_frame_num + snippet_duration)
        ffmpeg_extract_subclip(video_path, start_frame/fps, end_frame/fps, targetname=f"violations/red_light_violation_{violation_frame_num}.mp4")
        
        absolute_output_path = os.path.abspath(f"violations/red_light_violation_{violation_frame_num}.mp4")
        violationlist.append([f"red_light_violation_{violation_frame_num}","Red Light", place, datetime.now(),absolute_output_path])
        


    cap = cv2.VideoCapture(video_source)  # or 0 for camera
    violationlist=[]
    frame_counter = 0
    line_of_interest = 702
    skip_frames = 0

    while cap.isOpened():
        # Read a frame from the video stream
        ret, frame = cap.read()
        if not ret:
            break

        frame_counter += 1
        if skip_frames > 0:
            skip_frames = skip_frames - 1
            continue

        if frame_counter % 2 == 0:
            results = model(frame, verbose=False)  # results list
            boundaries = []
            vehicles=[]
            for r in results:
                detect = r.boxes.cls
                ids= r.boxes.id
                indexes = np.where(detect == 9)[0]
                detections = np.where(np.isin(detect, [2, 3, 5, 7]))[0]
                for i in indexes:
                    boundaries.append(r.boxes.xyxy[i])
                for i in detections:
                    vehicles.append(r.boxes.xyxy[i].int().tolist())

            #determine traffic light colours and draw the line of interest
            cropped_traffic_lights = crop_image(frame, boundaries)
            red_light = is_red_light(cropped_traffic_lights[0])
            #cv2.line(frame, (0, line_of_interest), (frame.shape[1], line_of_interest), (0, 0, 255), 2)

            if red_light == True:
                check = check_violation(vehicles,frame,frame_counter)
            if check ==  True:
                skip_frames = 4

            # Display the frame with the detected traffic light and classification
            #cv2.imshow("frame",frame)

            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
    return violationlist

# def main():
#     RLV_Model('videos\clip6.mp4','Portmore')

# if __name__ == "__main__":
#     main()