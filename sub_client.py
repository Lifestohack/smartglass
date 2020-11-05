import sys
import socket
import traceback
import cv2
import imagezmq
import threading
import numpy as np
import time
from pupil_detectors import Detector2D, Detector3D


# Helper class implementing an IO deamon thread
# When using the PUB/SUB pattern, the receiver of the frames will always receive all frames of the publisher. 
# This works as long as the receiver can keep up with the incoming data. If receiver is slow it can fall behind 
# and will not process the most recent frames from the publisher, but whatever is still in the receive queue of the zmq socket.
#A better approach (if network bandwidth is not most concerning) is to keep the socket open, receive every 
# frame in a dedicated IO thread, but only process the most recent one in a processing thread. 

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
        receiver.zmq_socket.set_hwm(1)
        while not self._stop:
            self._data = receiver.recv_jpg()
            self._data_ready.set()
        receiver.close()

    def close(self):
        self._stop = True

if __name__ == "__main__":
    # Receive from broadcast
    #hostname = "127.0.0.1"  # Use to receive from localhost
    hostname = "192.168.0.137"  # Use to receive from other computer
    port = 5555
    receiver = VideoStreamSubscriber(hostname, port)
    detector = Detector2D()
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
            # Due to the IO thread constantly fetching images, we can do any amount
            # of processing here and the next call to receive() will still give us
            # the most recent frame (more or less realtime behaviour)

            msg, frame = receiver.receive()
            receive_time = time.time()
            image = cv2.imdecode(np.frombuffer(frame, dtype='uint8'), -1)
            frame_time = msg
            latency = receive_time - frame_time
            print(latency)

            # Pupil detection happens here
            result = detector.detect(image)
            ellipse = result["ellipse"]

            # draw the ellipse outline onto the input image
            # note that cv2.ellipse() cannot deal with float values
            # also it expects the axes to be semi-axes (half the size)

            # Convert it to rgb to display it
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
