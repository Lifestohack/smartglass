import zmq
import sys
from time import sleep
import time
from divon import Publisher
from divon import VideoCapture
import cv2 as cv
import traceback

port = "5556"
pub = Publisher()

with_threading = False
capture = VideoCapture(1280, 720, with_threading)

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:5667")
time.sleep(0.2)

try:
    start_time = time.time()
    x = 1
    counter = 0
    while True:
        _, frame = capture.start().read()
        pub.send_array(socket, frame)
        counter+=1
        if (time.time() - start_time) > x :
            print("FPS: ", counter / (time.time() - start_time))
            counter = 0
            start_time = time.time()
        # cv.imshow('Frame', frame)
        # cv.waitKey(1) & 0xFF
        # break

except (KeyboardInterrupt, SystemExit):
    print('Exit due to keyboard interrupt')
except Exception as ex:
    print('Python error with no Exception handler:')
    print('Traceback error:', ex)
    traceback.print_exc()
finally:
    capture.stop()
    sys.exit(0)