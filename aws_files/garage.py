import RPi.GPIO as GPIO
import numpy as np
import cv2
from openalpr import Alpr
import time
import json
from rpi_lcd import LCD

import boto3
from boto3.dynamodb.conditions import Key, Attr

GPIO.setmode(GPIO.BCM)

GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)




# Import SDK packages
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from time import sleep

#intialise LCD
lcd = LCD()

# Custom MQTT message callback
def customCallback(client, userdata, message):
	print("Received a new message: ")
	print(message.payload)
	print("from topic: ")
	print(message.topic)
	print("--------------\n\n")
	
host = "certificates/abpl27ba00qyj-ats.iot.us-west-2.amazonaws.com"
rootCAPath = "certificates/rootca.pem"
certificatePath = "certificates/certificate.pem.crt"
privateKeyPath = "certificates/private.pem.key"

my_rpi = AWSIoTMQTTClient("basicPubSub")
my_rpi.configureEndpoint(host, 8883)
my_rpi.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

my_rpi.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
my_rpi.configureDrainingFrequency(2)  # Draining: 2 Hz
my_rpi.configureConnectDisconnectTimeout(10)  # 10 sec
my_rpi.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
my_rpi.connect()
my_rpi.subscribe("ush/carplate", 1, customCallback)
sleep(1)




alpr = Alpr("sg", "openalpr.conf", "runtime_data")
if not alpr.is_loaded():
    print("Error loading OpenALPR")
    sys.exit(1)

alpr.set_top_n(1)
alpr.set_default_region("sg")

from picamera import PiCamera
from time import sleep

camera = PiCamera()
camera.resolution = (800, 600)


message = {}




def is_authorise_carplate(carplate):
        dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
        table = dynamodb.Table('ush_authorise_carplate')

        response = table.scan()
    
        items = response['Items']


        for i in response['Items']:
            if(i['carplate'] == carplate):
                lcd.text('Welcome '+carplate,1)
                return "Yes"
        lcd.text('Unauthorised',1)
        lcd.text('License plate',2)
        sleep(2)
        return "No"


while True:

    #intialise last confidence variable
    last_confidence = 0
    
    button = GPIO.input(26)
    if button:
        print("Alerted")
        sleep(3)
        camera.capture('img.jpg')
        #my_rpi.publish("sensors/test", str("test"), 1)
        

        
        results = alpr.recognize_file("img.jpg")

        i = 0
                
        for plate in results['results']:
            i += 1
            print("Plate #%d" % i)
            print("   %12s %12s" % ("Plate", "Confidence"))
            for candidate in plate['candidates']:

                prefix = "-"
                if candidate['matches_template']:
                    prefix = "*"
                print("  %s %12s%12f" % (prefix, candidate['plate'], candidate['confidence'])) 
                if candidate['confidence'] > last_confidence:
                    message["carplate"] = candidate['plate']
                last_confidence = candidate['confidence']


            else:
                break;

        
        # check whether there is even a lisence plate being detect
        if last_confidence is not 0:
            message["timestamp"] = time.strftime("%d-%b-%Y %H:%M:%S")
            message["authorisation"] = is_authorise_carplate(message["carplate"])
            my_rpi.publish("ush/carplate", json.dumps(message), 1)
        else:
            lcd.text("No license plate detected",1)
            print ("no license plate detected")

        sleep(4)
        lcd.clear()





alpr.unload()

