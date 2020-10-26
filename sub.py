import cv2
import zmq
import base64
import numpy as np
import time

context = zmq.Context()
footage_socket = context.socket(zmq.SUB)
footage_socket.bind('tcp://127.0.0.1:5555')
footage_socket.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))

start_time = time.time()
x = 1 # displays the frame rate every 1 second
counter = 0

while True:
    counter+=1
    if (time.time() - start_time) > x :
        print("FPS: ", counter / (time.time() - start_time))
        counter = 0
        start_time = time.time()
    try:
        frame = footage_socket.recv()
        npimg = np.frombuffer(frame, dtype=np.uint8)
        #npimg = npimg.reshape(480,640,3)
        source = cv2.imdecode(npimg, 1)
        cv2.imshow("Stream", source)
        cv2.waitKey(1)

    except KeyboardInterrupt:
        cv2.destroyAllWindows()
        break
