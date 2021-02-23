from motion_detection import SingleMotionDetector

from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import render_template

import threading
import argparse
import datetime
import imutils
import time
import cv2

# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful when multiple browsers/tabs
# are viewing the stream)
outputFrame = None
lock = threading.Lock()

# initialize a flask object
app = Flask(__name__)

# initialize the video stream and allow the camera sensor to
# warmup
#vs = VideoStream(usePiCamera=1).start()	# for Raspberry Pi Camera
vs = VideoStream(src=0).start()
time.sleep(2.0)

@app.route("/")
def index():
	# return the rendered template
	return render_template("index.html")

def detect_motion(frameCount):
	# grab global references to the video stream, output frame, and
	# lock variables
	global vs, outputFrame, lock
	# initialize the motion detector and the total number of frames
	# read thus far
	md = SingleMotionDetector.SingleMotionDetector(accumWeight=0.1)
	total = 0

	# loop over frames from the video stream
	while True:

		# read frame from stream
		frame = vs.read()

		# resize frame
		frame = imutils.resize(frame, width=400)

		# convert frame to grayscale
		grayImage = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

		# blur the frame
		grayImage = cv2.GaussianBlur(grayImage, (7, 7), 0)

		# grab the current timestamp and draw it on the frame
		timestamp = datetime.datetime.now()
		cv2.putText(frame, timestamp.strftime(
			"%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
			cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)	

		# if the total number of frames has reached a sufficient
		# number to construct a reasonable background model, then
		# continue to process the frame
		if total > frameCount:
			# detect motion in the image
			motion = md.detect(grayImage)
			# check to see if motion was found in the frame
			if motion is not None:
				# unpack the tuple and draw the box surrounding the
				# "motion area" on the output frame
				(thresh, (minX, minY, maxX, maxY)) = motion
				cv2.rectangle(frame, (minX, minY), (maxX, maxY),
					(0, 0, 255), 2)
		
		# update the background model
		md.update(grayImage)

		# increment the total number of frames read thus far
		total += 1

		# acquire the lock, set the output frame; 
		# this ensures that outputFrame is not being read by a client while we're updating
		with lock:
			outputFrame = frame.copy()

# generator used to encode the outputFrame as JPEG data
def generate():
	# grab global references to the output frame and lock variables
	global outputFrame, lock
	# loop over frames from the output stream
	while True:
		# wait until the lock is acquired
		with lock:

			# check if the output frame is available, otherwise skip
			# the iteration of the loop
			if outputFrame is None:
				continue
			
			# encode the frame in JPEG format
			(flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
			
			# ensure the frame was successfully encoded
			if not flag:
				continue
		
		# yield the output frame in the byte format
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')

# The app.route signature tells Flask that this function is a URL endpoint 
# and that data is being served from http://your_ip_address/video_feed.
@app.route("/video_feed")
def video_feed():	# this function name is the parameter in the html image source.
	# return the response generated along with the specific media type (mime type)
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")

@app.route("/about1")
def about():
    return "<h1 style='color: red;'>I'm a red H1 heading!</h1>"

@app.route("/about2")
def about2():
    return """
    <h1 style='color: red;'>I'm a red H1 heading!</h1>
    <p>This is a lovely little paragraph</p>
    <code>Flask is <em>awesome</em></code>
    """
'''
@app.route("/fps")
def fps():
	return Reponse
'''
# check to see if this is the main thread of execution
if __name__ == '__main__':
	# construct the argument parser and parse command line arguments
	ap = argparse.ArgumentParser()
	# IP address of the system you are launching the webstream.py file from.
	ap.add_argument("-i", "--ip", type=str, required=True,
		help="ip address of the device")
	# Port number that Flask app will run on (typically 8000)
	ap.add_argument("-o", "--port", type=int, required=True,
		help="ephemeral port number of the server (1024 to 65535)")
	# Number of frames to accumulate and build the background moudel before motion detection is performed.
	# By default, we use 32 frames to build the background model.
	ap.add_argument("-f", "--frame-count", type=int, default=32,
		help="# of frames used to construct the background model")
	args = vars(ap.parse_args())


	# start a thread that will perform motion detection.
	# it will constantly be running and updating our outputFrame in the background.
	t = threading.Thread(target=detect_motion, args=(args["frame_count"],))
	t.daemon = True
	t.start()

	# start the flask app
	app.run(host=args["ip"], 
		port=args["port"], 
		debug=True,
		threaded=True, 
		use_reloader=False)
# release the video stream pointer
vs.stop()


