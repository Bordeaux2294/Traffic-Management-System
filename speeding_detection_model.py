import os
import cv2
import numpy as np
import supervision as sv

from tqdm import tqdm
from ultralytics import YOLO
from supervision.assets import VideoAssets, download_assets
from collections import defaultdict, deque
from datetime import datetime
import random

def process_video(source_video_path,video, confidence_threshold, iou_threshold, model_resolution, source, target, target_width, target_height, violations_folder):
    # Initialize view transformer
    class ViewTransformer:
        def __init__(self, source, target):
            self.m = cv2.getPerspectiveTransform(source.astype(np.float32), target.astype(np.float32))

        def transform_points(self, points):
            if points.size == 0:
                return points
            reshaped_points = points.reshape(-1, 1, 2).astype(np.float32)
            transformed_points = cv2.perspectiveTransform(reshaped_points, self.m)
            return transformed_points.reshape(-1, 2)

    # Initialize YOLO model
    model = YOLO('yolov8n.pt')

    # Get video information
    video_info = sv.VideoInfo.from_video_path(video_path=source_video_path)

    # Initialize frame generator
    frame_generator = sv.get_video_frames_generator(source_path=source_video_path)

    # Initialize view transformer
    view_transformer = ViewTransformer(source=source, target=target)

    # Initialize trackers and annotators
    byte_track = sv.ByteTrack(frame_rate=video_info.fps, track_thresh=confidence_threshold)
    thickness = 1
    text_scale = 1
    bounding_box_annotator = sv.BoundingBoxAnnotator(thickness=thickness, color_lookup=sv.ColorLookup.TRACK)
    label_annotator = sv.LabelAnnotator(text_scale=text_scale, text_thickness=thickness, text_position=sv.Position.BOTTOM_CENTER, color_lookup=sv.ColorLookup.TRACK)
    trace_annotator = sv.TraceAnnotator(thickness=thickness, trace_length=video_info.fps * 2, position=sv.Position.BOTTOM_CENTER, color_lookup=sv.ColorLookup.TRACK)
    polygon_zone = sv.PolygonZone(polygon=source, frame_resolution_wh=video_info.resolution_wh)
    coordinates = defaultdict(lambda: deque(maxlen=video_info.fps))

    os.makedirs(violations_folder, exist_ok=True)

    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    name=f"speeding_{current_time}.mp4"
    output_video_path = os.path.join(violations_folder, name)
    absolute_output_path = os.path.abspath(output_video_path)
    # Open target video
    with sv.VideoSink(output_video_path, video_info) as sink:
        # Loop over source video frames
        for frame in tqdm(frame_generator, total=video_info.total_frames):
            result = model(frame, imgsz=model_resolution, verbose=False)[0]
            detections = sv.Detections.from_ultralytics(result)

            # Filter out detections by class and confidence
            detections = detections[detections.confidence > confidence_threshold]
            detections = detections[detections.class_id != 0]

            # Filter out detections outside the zone
            detections = detections[polygon_zone.trigger(detections)]

            # Refine detections using non-max suppression
            detections = detections.with_nms(iou_threshold)

            # Pass detection through the tracker
            detections = byte_track.update_with_detections(detections=detections)

            points = detections.get_anchors_coordinates(anchor=sv.Position.BOTTOM_CENTER)

            # Calculate the detections position inside the target RoI
            points = view_transformer.transform_points(points=points).astype(int)

            # Store detections position
            for tracker_id, [_, y] in zip(detections.tracker_id, points):
                coordinates[tracker_id].append(y)

            # Format labels
            labels = []
            for tracker_id in detections.tracker_id:
                if len(coordinates[tracker_id]) < video_info.fps / 2:
                    labels.append(f"#{tracker_id}")
                else:
                    coordinate_start = coordinates[tracker_id][-1]
                    coordinate_end = coordinates[tracker_id][0]
                    distance = abs(coordinate_start - coordinate_end)
                    time = len(coordinates[tracker_id]) / video_info.fps
                    speed = distance / time * 3.6
                    label_color = sv.Color.red() if speed > 100 else sv.ColorLookup.TRACK
                    if speed > 100:
                        labels.append(f"#{tracker_id} {int(speed)} km/h")
                    else:
                        labels.append(f"#{tracker_id}")

            # Annotate frame
            annotated_frame = frame.copy()
            annotated_frame = trace_annotator.annotate(scene=annotated_frame, detections=detections)
            annotated_frame = bounding_box_annotator.annotate(scene=annotated_frame, detections=detections)
            annotated_frame = label_annotator.annotate(scene=annotated_frame, detections=detections, labels=labels)
            
            # Add frame to target video
            sink.write_frame(annotated_frame)

    # Returning the required information
    places = ['Kingston','Portmore','St. James', 'St Elizabeth']
    random_index = random.randint(0, len(places) - 1)
    info=[]
    info_list = [name, "Speeding",places[random_index], datetime.now(), absolute_output_path]
    info.append(info_list)
    return info


