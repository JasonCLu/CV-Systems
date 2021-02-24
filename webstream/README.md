## The Big Picture:

WEBCAM -> CV/Image Processing -> HTTP Website


## The Steps and Tools:

1) Get the video stream from laptop camera (using OpenCV).
2) Apply motion detection on frames from video stream (using OpenCV).
3) Create a simple website (using Python Flask Framework and HTML).
4) Display processed frames to website (using Python Flask Framework and HTML)


## The Required Python Packages:
#### Use these commands in the terminal to install packages:

1) pip install flask
2) pip install imutils
3) pip install numpy
4) pip install opencv-contrib-python


## To Run:

1) run 'python3 webstreaming.py --ip 0.0.0.0 --port 8000' in terminal.
2) copy the routing address found in the log info. (e.g. http://0.0.0.0:8000/).
3) open browser of choice and open webpage with the routing address.
