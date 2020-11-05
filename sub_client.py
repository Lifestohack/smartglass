"""pub_sub_receive.py -- receive OpenCV stream using PUB SUB."""

import sys

import socket
import traceback
import cv2
from imutils.video import VideoStream
import imagezmq
import threading
import numpy as np
import time
from pupil_detectors import Detector2D, Detector3D

detector = Detector2D()

# Helper class implementing an IO deamon thread
class VideoStreamSubscriber:

    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port
        self._stop = False
        self._data_ready = threading.Event()
        self._thread = threading.Thread(target=self._run, args=())
        self._thread.daemon = True
        self._thread.start()

    def receive(self, timeout=1500000.0):
        flag = self._data_ready.wait(timeout=timeout)
        if not flag:
            raise TimeoutError(
                "Timeout while reading from subscriber tcp://{}:{}".format(self.hostname, self.port))
        self._data_ready.clear()
        return self._data

    def _run(self):
        receiver = imagezmq.ImageHub("tcp://{}:{}".format(self.hostname, self.port), REQ_REP=False)
        #print(receiver.zmq_socket.hwm)
        #receiver.zmq_socket.set_hwm(1)
        #print(receiver.zmq_socket.hwm)
        while not self._stop:
            self._data = receiver.recv_jpg()
            self._data_ready.set()
        receiver.close()

    def close(self):
        self._stop = True

# Simulating heavy processing load
def limit_to_2_fps():
    time.sleep(0.5)

if __name__ == "__main__":
    # Receive from broadcast
    # There are 2 hostname styles; comment out the one you don't need
    #hostname = "127.0.0.1"  # Use to receive from localhost
    hostname = "192.168.0.137"  # Use to receive from other computer
    port = 5555
    receiver = VideoStreamSubscriber(hostname, port)

    try:
        start_time = time.time()
        x = 1
        counter = 0
        font                   = cv2.FONT_HERSHEY_SIMPLEX
        bottomLeftCornerOfText = (0,30)
        fontScale              = 1
        fontColor              = (255,255,255)
        lineType               = 1
        fps = 0
        while True:
            msg, frame = receiver.receive()
            receive_time = time.time()
            image = cv2.imdecode(np.frombuffer(frame, dtype='uint8'), -1)
            frame_time = msg
            latency = receive_time - frame_time
            print(latency)
            #print(str(receive_time) + " " + str(frame_time) + "=" + str(latency))
            # Due to the IO thread constantly fetching images, we can do any amount
            # of processing here and the next call to receive() will still give us
            # the most recent frame (more or less realtime behaviour)

            # Uncomment this statement to simulate processing load
            # limit_to_2_fps()   # Comment this statement out to run full speeed
            
            result = detector.detect(image)
            ellipse = result["ellipse"]

            # draw the ellipse outline onto the input image
            # note that cv2.ellipse() cannot deal with float values
            # also it expects the axes to be semi-axes (half the size)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            cv2.ellipse(
                image,
                tuple(int(v) for v in ellipse["center"]),
                tuple(int(v / 2) for v in ellipse["axes"]),
                ellipse["angle"],
                0, 360, # start/end angle for drawing
                (0, 0, 255) # color (BGR): red
            )
            cv2.putText(image, str(fps) +"  " +str(latency), 
                bottomLeftCornerOfText, 
                font, 
                fontScale,
                fontColor,
                lineType)
            cv2.imshow("Pub Sub Receive", image)
            cv2.waitKey(1)

            counter = counter + 1
            seconds = time.time() - start_time
            if seconds > x:
                #print("FPS: ", counter, "per", seconds)
                fps = counter
                counter = 0
                start_time = time.time()

    except (KeyboardInterrupt, SystemExit):
        print('Exit due to keyboard interrupt')
    except Exception as ex:
        print('Python error with no Exception handler:')
        print('Traceback error:', ex)
        traceback.print_exc()
    finally:
        receiver.close()
        sys.exit(0)
