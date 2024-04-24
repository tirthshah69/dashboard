import cv2
import os
import numpy as np
from ultralytics import YOLO
from werkzeug.utils import secure_filename
from base import app
from base.com.vo.detection_vo import LoginVO, DetectionVO
from base.com.dao.detection_dao import LoginDAO, DetectionDAO
from collections import defaultdict
import torch
import cvzone
import time


class PerformDetection:
    def __init__(self, model_name):
        self.model_name = model_name
        self.model_path = f'base/static/models/{self.model_name}.pt'
        self.model = YOLO(self.model_path)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.detection_service_output = {
            'detection_stats': defaultdict(),
            'detection_datetime': None
        }
        if self.model_name == 'cattle':
            self.classes = [15, 16, 17, 18, 19, 20, 21, 22, 23]
        elif self.model_name == 'pothole':
            self.classes = [1]
        else:
            self.classes = [0]

    def image_detection_service(self, input_file_path, output_file_path):
        try:
            image = cv2.imread(input_file_path)
            image = cv2.resize(image, (720, 480))
            results = self.model.predict(image, classes=self.classes,
                                    device=self.device)
            if results[0].boxes is not None:
                boxes = results[0].boxes.xyxy.cpu()
                for box in boxes:
                    x1, y1, x2, y2 = box
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    cv2.rectangle(image, (x1, y1), (x2, y2), (255, 0,
                                                              0), 3)
            else:
                boxes = results[0].obb.xyxyxyxy.cpu()
                for box in boxes:
                    points = np.array(box, np.int32)
                    points = points.reshape((-1, 1, 2))
                    cv2.polylines(image, [points], isClosed=True,
                                  color=(255, 0, 0), thickness=3)
            counts = len(results[0])

            if (self.detection_service_output.get('detection_datetime') is
                    None and counts > 0):
                self.detection_service_output['detection_datetime'] = int(
                    time.time())

            cv2.imwrite(output_file_path, image)

            if self.model_name == 'pothole':
                self.detection_service_output['detection_stats'][
                    'pothole_counts'] = counts
            elif self.model_name == 'cattle':
                self.detection_service_output['detection_stats'][
                    'cattle_counts'] = counts
            elif self.model_name == 'garbage':
                if counts > 0:
                    self.detection_service_output['detection_stats'][
                        'is_garbage'] = True
                else:
                    self.detection_service_output['detection_stats'][
                        'is_garbage'] = False
            return self.detection_service_output

        except Exception as e:
            return {'error': str(e)}

    def video_detection_service(self, input_file_path, output_file_path):
        try:

            cap = cv2.VideoCapture(input_file_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            codec = int(cap.get(cv2.CAP_PROP_FOURCC))
            fourcc = cv2.VideoWriter_fourcc(*chr(codec & 0xFF), chr((codec >> 8) & 0xFF), chr((codec >> 16) & 0xFF), chr((codec >> 24) & 0xFF))

            out = cv2.VideoWriter(output_file_path, fourcc, 1, (width, height))

            actual_fps = int(fps)
            frame_number = 0

            garbage_flag = False
            min_count = float('inf')
            max_count = 0

            while cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    frame_number += 1

                    if frame_number % actual_fps == 0:

                        results = self.model.predict(frame,
                                                     classes=self.classes,
                                                device=self.device)
                        counts = len(results[0])

                        if results[0].boxes is not None:
                            boxes = results[0].boxes.xyxy.cpu()
                            for box in boxes:
                                x1, y1, x2, y2 = box
                                x1, y1, x2, y2 = int(x1), int(y1), int(
                                    x2), int(y2)
                                cv2.rectangle(frame, (x1, y1), (x2, y2),
                                              (255, 0, 0), 3)
                        else:
                            boxes = results[0].obb.xyxyxyxy.cpu()
                            for box in boxes:
                                points = np.array(box, np.int32)
                                points = points.reshape((-1, 1, 2))
                                cv2.polylines(frame, [points], isClosed=True,
                                              color=(255, 0, 0), thickness=3)

                        if (self.detection_service_output.get(
                                'detection_datetime') is
                                None and counts > 0):
                            self.detection_service_output[
                                'detection_datetime'] = int(
                                time.time())

                        if self.model_name == 'pothole':
                            min_count = min(min_count, counts)
                            self.detection_service_output['detection_stats'][
                            'minimum_pothole_counts'] = min_count
                            max_count = max(max_count, counts)
                            self.detection_service_output[
                            'detection_stats']['maximum_pothole_counts'] = max_count
                        elif self.model_name == 'cattle':
                            min_count = min(min_count, counts)
                            self.detection_service_output['detection_stats'][
                                'minimum_cattle_counts'] = min_count
                            max_count = max(max_count, counts)
                            self.detection_service_output[
                                'detection_stats'][
                                'maximum_cattle_counts'] = max_count
                        elif self.model_name == 'garbage':
                            if garbage_flag == False and counts > 0:
                                self.detection_service_output[
                                    'detection_stats'][
                                    'is_garbage'] = True
                                garbage_flag = True

                        out.write(frame)


                else:
                    break

            cap.release()
            out.release()
            if not garbage_flag and self.model_name == 'garbage':
                self.detection_service_output[
                    'detection_stats'][
                    'is_garbage'] = False
                
            if self.model_name == 'pothole' and (self.detection_service_output[
                                'detection_stats'][
                                'maximum_pothole_counts'] > 0 and self.detection_service_output[
                                'detection_stats'][
                                'minimum_pothole_counts'] == 0):
                self.detection_service_output[
                                'detection_stats'][
                                'minimum_pothole_counts'] = 1
                
            if self.model_name == 'cattle' and ( self.detection_service_output[
                                'detection_stats'][
                                'maximum_cattle_counts'] > 0 and self.detection_service_output[
                                'detection_stats'][
                                'minimum_cattle_counts'] == 0):
                self.detection_service_output[
                                'detection_stats'][
                                'minimum_cattle_counts'] = 1


            return self.detection_service_output
        except Exception as e:
            return {'error': str(e)}

