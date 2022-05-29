from time import gmtime, strftime
from picamera import PiCamera
import json as simplejson
import time
import os
import boto3

def takePhoto(userName):

    count = 5
    camera = PiCamera()
    camera.vflip = True
    camera.hflip = True
    directory = os.path.dirname(os.path.realpath(__file__)) + '/' + 'face'
    if not os.path.exists(directory):
        os.makedirs(directory)

    print '[+] A photo will be taken in 5 seconds...'

    for i in range(count):
        print (count - i)
        time.sleep(1)

    milli = int(round(time.time() * 1000))
    image1 = '{0}/image_{1}.jpg'.format(directory, milli)
    camera.capture(image1)
    print 'Your image was saved to %s' % image1
    camera.close()

    print('[+] Adding Image to Container')

    client = boto3.client('rekognition')
    with open(image1, 'rb') as image:
        response = client.index_faces(Image={'Bytes': image.read()}, CollectionId='home', ExternalImageId=userName, DetectionAttributes=['ALL'])

    print('[+] Finish Uploading Image to Container')



def deletePhoto(userName):
    client = boto3.client('rekognition')
    print('[+] Deleting Face from Container')
    #response = client.delete_faces(CollectionId='home', FaceIds=[args.id])
    response = client.delete_faces(CollectionId='home', FaceIds=['d3c239cd-b279-4506-b6f2-509465b8733d'])
    print('[+] Finish Deleting Image from Container')

  