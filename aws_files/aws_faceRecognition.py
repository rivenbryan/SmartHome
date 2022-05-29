#!/usr/bin/env python
from rpi_lcd import LCD
from picamera import PiCamera
import time
import os

import boto3 as b3
from argparse import ArgumentParser
from time import gmtime, strftime


###################################################################################

print("-----------------------------------------------------------")
print("[+] Second Authentication: Facial Recognition")

lcd = LCD()
## Take a Photo
print("[+] Starting to take a photo..")
count = 5
camera = PiCamera()
camera.vflip = True
camera.hflip = True
directory = '/home/pi/Desktop/Assignment2/pi-detector/faces'

if not os.path.exists(directory):
    os.makedirs(directory)

print '[+] A photo will be taken in 5 seconds...'

lcd.text('Scanning for ', 1)
lcd.text('nearby faces...', 2)
time.sleep(5)

##image = '{0}/image_{1}.jpg'.format(directory, milli)
image = '{0}/image.jpg'.format(directory)
camera.capture(image)
print 'Your image was saved to %s' % image

camera.close() 
###################################################################################


def get_client():
    return b3.client('rekognition')


def check_face(client, file):
    face_detected = False
    with open(file, 'rb') as image:
        response = client.detect_faces(Image={'Bytes': image.read()})
        if (not response['FaceDetails']):
            face_detected = False
        else: 
            face_detected = True

    return face_detected, response

def check_matches(client, file, collection):
    face_matches = False
    with open(file, 'rb') as image:
        response = client.search_faces_by_image(CollectionId=collection, Image={'Bytes': image.read()}, MaxFaces=1, FaceMatchThreshold=85)
        if (not response['FaceMatches']):
            face_matches = False
        else:
            face_matches = True

    return face_matches, response


client = get_client()

capturedImage = "/home/pi/Desktop/Assignment2/pi-detector/faces/image.jpg"
collection = "home"

print '[+] Running face checks against image...'
result, resp = check_face(client, capturedImage)

## Checks Recognition

if (result):
	print '[+] Face(s) detected with %r confidence...' % (round(resp['FaceDetails'][0]['Confidence'], 2))
	print '[+] Checking for a face match...'
	resu, res = check_matches(client, capturedImage, collection)

	if (resu):
		print '[+] Identity matched %s with %r similarity and %r confidence...' % (res['FaceMatches'][0]['Face']['ExternalImageId'], round(res['FaceMatches'][0]['Similarity'], 1), round(res['FaceMatches'][0]['Face']['Confidence'], 2))
		lcd.text('Door Opened!', 1)
		lcd.text('Welcome, '+ res['FaceMatches'][0]['Face']['ExternalImageId'] , 2)
		time.sleep(5)
		lcd.clear()

		import aws_temperature
	else:
		print '[-] No face matches detected...' 
		lcd.text('Access Denied!', 1)
		lcd.text('No face matches detected...', 2)
		time.sleep(3)
		lcd.clear()
		exit()
else:
    print "[-] No faces detected..."
    lcd.text('Access Denied!', 1)
    lcd.text('No face detected...', 2)
    time.sleep(3)
    lcd.clear()
    exit()

