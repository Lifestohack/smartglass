import sys
import zmq
import cv2 as cv
import traceback
from divon import Publisher

port = "5556"

pub = Publisher()

# Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.setsockopt(zmq.SUBSCRIBE, b"")
socket.connect("tcp://localhost:5667")

try:
    while True:
        frame = pub.recv_array(socket)
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