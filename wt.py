import math
import cv2
import cvzone
import numpy as np
import os
from datetime import datetime

def detect_turn(video_path, output_video_path):
    class Tracker:
        def __init__(self):
            # Store the center positions of the objects
            self.center_points = {}
            # Keep the count of the IDs
            # each time a new object id detected, the count will increase by one
            self.id_count = 0


        def update(self, objects_rect):
            # Objects boxes and ids
            objects_bbs_ids = []

            # Get center point of new object
            for rect in objects_rect:
                x, y, w, h = rect
                cx = (x + x + w) // 2
                cy = (y + y + h) // 2

                # Find out if that object was detected already
                same_object_detected = False
                for id, pt in self.center_points.items():
                    dist = math.hypot(cx - pt[0], cy - pt[1])

                    if dist < 35:
                        self.center_points[id] = (cx, cy)
                        print(self.center_points) #
                        objects_bbs_ids.append([x, y, w, h, id])
                        same_object_detected = True
                        break

                # New object is detected we assign the ID to that object
                if same_object_detected is False:
                    self.center_points[self.id_count] = (cx, cy)
                    objects_bbs_ids.append([x, y, w, h, self.id_count])
                    self.id_count += 1

            # Clean the dictionary by center points to remove IDS not used anymore
            new_center_points = {}
            for obj_bb_id in objects_bbs_ids:
                _, _, _, _, object_id = obj_bb_id
                center = self.center_points[object_id]
                new_center_points[object_id] = center

            # Update dictionary with IDs not used removed
            self.center_points = new_center_points.copy()
            return objects_bbs_ids

    # Initialize the video capture, saving output to a video
    video_path = 'wrongturns.mp4'
    cap = cv2.VideoCapture(video_path)

    #create a background subtractor
    fgbg = cv2.createBackgroundSubtractorMOG2()
    area1=[(71, 212),(329, 247),(324, 270),(31, 236)]
    area2=[(280, 240),(322, 141),(357, 146),(319, 251)]
    tracker=Tracker()
    #save id and position of vehicles
    vid={}
    counter=[]
    def save_full_frame(frame):
    # Create a folder with the current date and time as the folder name
        current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
        folder_name = f"violations"
        os.makedirs(folder_name, exist_ok=True)

        # Save the entire frame
        image_filename = os.path.join(folder_name, f"frame_{current_datetime}.jpg")
        cv2.imwrite(image_filename, frame)
    while True:
        ret, frame = cap.read()

        if not ret:
            break
        #frame=cv2.resize(frame,(1020,500))
        frame=cv2.resize(frame,(450,360))

        # Apply background subtraction
        #fgbg represents clear bg, subtracting the background
        fgmask = fgbg.apply(frame)

        #threshold the foreground mask
        _, thresh = cv2.threshold(fgmask, 250, 250, cv2.THRESH_BINARY)

        # Find contours in the thresholded image
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Draw rectangles around moving objects
        list=[]
        for contour in contours:
            if cv2.contourArea(contour) >=7:  # Adjust the area threshold as needed
                x, y, w, h = cv2.boundingRect(contour)
                list.append([x,y,w,h])
        bbox_idx=tracker.update(list)
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
                    cv2.rectangle(frame, (x1, y1), (x1 + w1, y1 + h1), (255, 255, 255), 1)
                    cv2.circle(frame,(cx,cy),7,(255, 255, 255,-1))
                    cvzone.putTextRect(frame,f'wrong turn',(x1,y1),.5,1,
                                       colorT=(255,255, 255), colorR=(1, 1, 1),
                                       font=cv2.FONT_HERSHEY_SIMPLEX,
                                       offset=10)
                        
                    if counter.count(id)==0:
                        counter.append(id)
                        save_full_frame(frame)
  

        cv2.polylines(frame,[np.array(area1,np.int32)],True,(0,255,0),2)
        cv2.polylines(frame,[np.array(area2,np.int32)],True,(0,0,255),2)
        

        p=len(counter)
        #add text with counter to screen
        cvzone.putTextRect(frame,f'Wrong turns: {p}',(10,50),1,2,
            colorT=(255,255, 255), colorR=(1, 1, 1),
            font=cv2.FONT_HERSHEY_SIMPLEX,
            offset=10,
            border=1, colorB=(255, 255, 255))
        
            
        cv2.imshow("frame",frame)
        
        if cv2.waitKey(1) & 0xFF == 27:  # Press 'Esc' to exit
            break
        

    
    # Release the video capture and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()
    #out.release()
    
    info_list = ["wrongturns.mp4", "illegal_turn", "Kingston", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), output_video_path]
    return info_list
   

result_info = detect_turn('wrongturns.mp4', 'wrongway.mp4')
print(result_info)
