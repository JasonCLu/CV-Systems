The big picture:

WEBCAM -> CV/Image Processing -> HTTPS Website


The steps:

1) Get the video stream from the laptop camera (using OpenCV).
2) Apply object detection on frames from video stream (using OpenCV).
3) Create a simple website (using Python Flask Framework and HTML).
4) Display processed frames to website (using Python Flask Framework and HTML)


Before running, these python packages are required:
$ pip install flask
$ pip install imutils
$ pip install numpy
$ pip install opencv-contrib-python
