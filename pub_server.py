"""pub_sub_broadcast.py -- broadcast OpenCV stream using PUB SUB."""

import sys

import socket
import traceback
import time
import cv2
import imagezmq
from picamera import PiCamera
from picamera.array import PiRGBArray
from picamera.array import PiYUVArray
import numpy as np
import threading

# Helper class implementing an IO deamon thread
class StartThreadToStream:

    def __init__(self, newframe, frame):
        self.newframe = newframe
        self.frame = frame
        self._stop = False
        self.duplicate = []
        self._thread = threading.Thread(target=self._run, args=())
        self._thread.daemon = True
        self._thread.start()

    def _run(self):
        # JPEG quality, 0 - 100
        x = 1
        counter = 0
        start_time = time.time()
        jpeg_quality = 100
        while not self._stop:
            if self.newframe == True:
                self.newframe = False
                f = self.frame[:,:,0]
                a = time.time()
                _, jpg_buffer = cv2.imencode(
                    ".jpg", f, [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality])
                sender.send_jpg(time.time(), jpg_buffer)
                b = time.time()
                c = b - a 
                counter = counter + 1
                seconds = time.time() - start_time
                if seconds > x:
                    print("FPS Thread: ", counter, "per", seconds)
                    counter = 0
                    start_time = time.time()
            else:
                time.sleep(0.0001)
                pass

    def dataready(self, frame):
        self.newframe = True
        self.frame = frame
        #self.duplicate = frame

    def close(self):
        self._stop = True

def NonThreadedSend(start_time, counter):
    jpeg_quality = 100
    #_, jpg_buffer = cv2.imencode(
    #        ".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality])
    #sender.send_jpg(time.time(), jpg_buffer)
    counter = counter + 1
    seconds = time.time() - start_time
    if seconds > 1:
        print("FPS: ", counter, "per", seconds)
        counter = 0
        start_time = time.time()
    return start_time, counter


if __name__ == "__main__":
    # Publish on port
    port = 5555
    sender = imagezmq.ImageSender("tcp://*:{}".format(port), REQ_REP=False)
    print("Input stream opened")
    resolution =  (320, 240)
    framerate = 90
    rpi_name = socket.gethostname()
    # initialize the stream
    camera = PiCamera()
    time.sleep(2.0)  # Warmup time; needed by PiCamera on some RPi's
    # set camera parameters
    camera.resolution = resolution
    camera.framerate = framerate
    camera.rotation = 180
    #rawCapture = PiRGBArray(camera, size=resolution)
    rawCapture = PiYUVArray(camera, size=resolution)
    #self.rawCapture = PiBayerArray(self.camera)
    stream = camera.capture_continuous(rawCapture,
        format="yuv", use_video_port=True)
    counter = 0
    start_time = time.time()
    streamimage = StartThreadToStream(False, [])
    try:
        for f in stream:
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            frame = f.array            
            streamimage.dataready(frame)
            #start_time, counter = NonThreadedSend(start_time, counter)
            rawCapture.truncate(0)


    except (KeyboardInterrupt, SystemExit):
        print('Exit due to keyboard interrupt')
    except Exception as ex:
        print('Python error with no Exception handler:')
        print('Traceback error:', ex)
        traceback.print_exc()
    finally:
        #capture.stop()
        sender.close()
        sys.exit(0)