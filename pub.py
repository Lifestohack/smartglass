import base64
import cv2
import zmq
import numpy as np
import time

context = zmq.Context()
footage_socket = context.socket(zmq.PUB)
footage_socket.connect('tcp://127.0.0.1:5555')

camera = cv2.VideoCapture(0)  # init the camera
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

while True:
        try:
                grabbed, frame = camera.read()  # grab the current frame
                #frame = cv2.resize(frame, (640, 480))  # resize the frame
                encoded, buffer = cv2.imencode('.jpg', frame)
                footage_socket.send(buffer)
        except KeyboardInterrupt:
                camera.release()
                cv2.destroyAllWindows()
                break
