
import cv2
import os

from picamera.array import PiRGBArray
from picamera import PiCamera

# cam = cv2.VideoCapture(0)
# cam.set(3, 640) # set video width
# cam.set(4, 480) # set video height
# Setup the camera
camera = PiCamera()
camera.resolution = ( 640, 480 )
camera.framerate = 2#帧速率
#每秒显示帧数(Frames per Second，简称：FPS）
rawCapture = PiRGBArray( camera, size=( 640, 480 ) )

face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# For each person, enter one numeric face id
face_id = input('\n Input user id end press <enter> ==>  ')

print("\n [INFO] Initializing face capture. Look the camera and wait ...")
# Initialize individual sampling face count
count = 0

# while(True):
for frame in camera.capture_continuous( rawCapture, format="bgr", use_video_port=True ):
    img = frame.array
   # img = cv2.flip(img, -1) # flip video image vertically
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(gray, 1.3, 5)

    for (x,y,w,h) in faces:

        cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)     
        count += 1

        # Save the captured image into the datasets folder
        cv2.imwrite("dataset/User." + str(face_id) + '.' + str(count) + ".jpg", gray[y:y+h,x:x+w])

        cv2.imshow('image', img)

    k = cv2.waitKey(100) & 0xff # Press 'ESC' for exiting video
    if k == 27:
        break
    elif count >= 30: # Take 30 face sample and stop video
         break
    # Clear the stream in preparation for the next frame
    rawCapture.truncate( 0 )
# Do a bit of cleanup
print("\n [INFO] Successfully stored user information with id {}".format(face_id))
print("\n [INFO] Exiting Program and cleanup stuff")

cv2.destroyAllWindows()


