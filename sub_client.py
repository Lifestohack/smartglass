import sys
import zmq
import cv2 as cv
import traceback
from divon import Publisher
import time

pub = Publisher()

# Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.setsockopt(zmq.SUBSCRIBE, b"")
socket.connect("tcp://localhost:5667")

try:
    start_time = time.time()
    x = 1
    counter = 0
    while True:
        frame = pub.recv_array(socket)
        counter+=1
        if (time.time() - start_time) > x :
            print("FPS: ", counter / (time.time() - start_time))
            counter = 0
            start_time = time.time()
        cv.imshow('Frame', frame)
        cv.waitKey(1) & 0xFF
except (KeyboardInterrupt, SystemExit):
    print('Exit due to keyboard interrupt')
except Exception as ex:
    print('Python error with no Exception handler:')
    print('Traceback error:', ex)
    traceback.print_exc()
finally:
    cv.destroyAllWindows()
    sys.exit(0)