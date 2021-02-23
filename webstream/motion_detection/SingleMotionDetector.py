import numpy as np
import imutils
import cv2

class SingleMotionDetector:
	
	def __init__(self, accumWeight=0.5): #  accumWeight = [0,1]

		# store the accumulated weight factor (the larger the factor, 
		# the less the background will be factored in when accumulating the weighted average)
		self.accumWeight = accumWeight

		# initialize the background model
		self.bg = None

	# accept image frame and compute the weighted average
	def update(self, image):
		# if the background model is None, initialize it (as a copy of the frame)
		if self.bg is None:
			self.bg = image.copy().astype("float")
			return

		# update the background model by accumulating the weighted average
		cv2.accumulateWeighted(image, self.bg, self.accumWeight)

	# motion detection
	def detect(self, image, tVal=25):
		# compute the absolute difference between the background model and the image passed in
		delta = cv2.absdiff(self.bg.astype("uint8"), image)

		# threshold the delta image; any pixel value greater than tVal is set to 255 (white); less than will be set to 0 (black)
		thresh = cv2.threshold(delta, tVal, 255, cv2.THRESH_BINARY)[1]

		# perform a series of erosions and dilations to remove small blobs (likely due to reflections or rapid changes in light)
		thresh = cv2.erode(thresh, None, iterations=2)
		thresh = cv2.dilate(thresh, None, iterations=2)

		# find contours in the thresholded image
		contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		contours = imutils.grab_contours(contours)

		# initialize the min and max bounding box regions for motion
		(minX, minY) = (np.inf, np.inf)
		(maxX, maxY) = (-np.inf, -np.inf)

		# if no contours were found (no motion detected), return None
		if len(contours) == 0:
			return None
		
		# otherwise (motion is detected), loop over the contours
		for c in contours:
			# compute the bounding box of the contour and use it to
			# update the minimum and maximum bounding box regions
			(x, y, w, h) = cv2.boundingRect(c)
			(minX, minY) = (min(minX, x), min(minY, y))
			(maxX, maxY) = (max(maxX, x + w), max(maxY, y + h))
		
		# return a tuple of the thresholded image along with bounding box
		return (thresh, (minX, minY, maxX, maxY))




