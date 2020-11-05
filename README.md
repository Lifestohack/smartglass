# smartglass

This is just tested on Ubuntu 18.04 LTS.

Some dependencies should be installed before using it.

```sh
sudo apt install -y pkg-config git cmake build-essential nasm wget python3-setuptools libusb-1.0-0-dev  python3-dev python3-pip python3-numpy python3-scipy libglew-dev libtbb-dev

# ffmpeg >= 3.2
sudo apt install -y libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev libswscale-dev libavresample-dev ffmpeg x264 x265 libportaudio2 portaudio19-dev

# OpenCV >= 3
sudo apt install -y python3-opencv libopencv-dev

# 3D Eye model dependencies
sudo apt install -y libgoogle-glog-dev libatlas-base-dev libeigen3-dev
sudo apt install -y libceres-dev
```


```sh
# Upgrade pip to latest version. This is necessary for some dependencies.

python -m pip install --upgrade pip

pip install cysignals
pip install cython
pip install pupil-detectors
pip install pyzmq
```