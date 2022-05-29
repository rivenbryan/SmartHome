from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from boto3.dynamodb.conditions import Key, Attr
from rpi_lcd import LCD
from time import sleep
from picamera import PiCamera
import RPi.GPIO as GPIO
import time 
import random
import boto3
import telepot

###################################################################################################
# Custom MQTT message callback
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")

def telegrambot(): # Telegram Bot to receive image from RaspberryPi

    camera = PiCamera()
    print("Telegram Bot")
    my_bot_token = '729641371:AAFgRD3BpngMq4Pngp_VZOU_Hc7A7uDFQAM'
    bot = telepot.Bot(my_bot_token)
    camera.capture('/home/pi/Desktop/Assignment2/image1.jpg')
    bot.sendPhoto(chat_id=414346130, photo=open('/home/pi/Desktop/Assignment2/image1.jpg', 'rb'))
    print('Capture Intruder Image')
    camera.close()
    print("End of Telegram Bot")


host = "abpl27ba00qyj-ats.iot.us-west-2.amazonaws.com"
rootCAPath = "certificates/rootca.pem"
certificatePath = "certificates/certificate.pem.crt"
privateKeyPath = "certificates/private.pem.key"

print("-----------------------------------------------------------")
print("[+] First Authentication: KeyPad")

my_rpi = AWSIoTMQTTClient("basicPubSub")
my_rpi.configureEndpoint(host, 8883)
my_rpi.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

my_rpi.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
my_rpi.configureDrainingFrequency(2)  # Draining: 2 Hz
my_rpi.configureConnectDisconnectTimeout(10)  # 10 sec
my_rpi.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
my_rpi.connect()
my_rpi.subscribe("ush/keypad/pin", 1, customCallback)
sleep(2)

###############################################################################################

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('ush_pin')
#opendoor = 0
response = table.query(
    KeyConditionExpression=Key('deviceid').eq('deviceid_bryantay'))

for i in response['Items']:
    opendoor = i['pin']
    dbThreshold = i['threshhold']
    print("[+] Pin fom Database is " + str(opendoor))
    print("[+] Threshold is " + dbThreshold)

#################################################################################################

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

MATRIX = [[1,2,3,'A'],
     [4,5,6,'B'],
     [7,8,9,'C'],
     ['*',0,'#','D']]

ROW = [7,11,13,15]
COL = [12,16,18,22]

lcd = LCD()
threshhold = 0

keypress = ""
feature = False


for j in range(4):
    GPIO.setup(COL[j], GPIO.OUT)
    GPIO.output(COL[j], 1)

for i in range(4):
    GPIO.setup(ROW[i], GPIO.IN, pull_up_down = GPIO.PUD_UP)

print("[+] KeyPad Program Starting:")
try:
    while(True):
        
        for j in range(4):
            GPIO.output(COL[j],0)

            lcd.text('4-Pin Password', 1)

            for i in range(4):
                if GPIO.input(ROW[i]) == 0:
                    print MATRIX[i][j]
                    
                    keypress = keypress + str(MATRIX[i][j])
                    
                    lcd.text(str(keypress), 2)

                    if len(keypress) == 4:
                                if keypress == str(opendoor): ## Authenticated

                                    print("<Correct 4-Pin Password>")
                                    
                                    lcd.clear()
                                    lcd.text('Access Granted', 1)
                                    time.sleep(3)
                                    lcd.clear()

                                    ## Facial Recognition
                                    import aws_faceRecognition # Hop on into next file
                                   

                                else: # Error
                                    print("<Incorrect 4-Pin Password>")

                                    lcd.text('Wrong Pin.', 1)
                                    lcd.text('Please try again.',2)
                                    time.sleep(3)
                                    lcd.clear()
                                    keypress ="" ## reset string 
                                    threshhold+=1
                                    print("number of threshhold " + str(threshhold))
                                    print("number of database threshhold " + str(dbThreshold))
                                    if str(threshhold) == str(dbThreshold):
                                        print("[-] Maximum Number of Threshhold hits.")
                                        telegrambot()
                                        lcd.text("WARNING!",1)
                                        lcd.text("DOOR LOCKED",2)
                                        time.sleep(3)


                                         #  Generate 4-pin Nnumber
                                        newpin = random.randint(1111,9999)
                                        print("[+] New Pin is " + str(newpin))

                                        lcd.text("PIN RESET", 1)
                                        lcd.text("Key in new Pin", 2)
                                        time.sleep(5)
                                        lcd.clear()
                                           
                                        # Update into Database
                                        table.update_item(
                                            Key={
                                            'deviceid': 'deviceid_bryantay'
                                            },
                                            UpdateExpression='SET pin = :val1',
                                            ExpressionAttributeValues={
                                            ':val1': newpin
                                            }
                                            )
                                        opendoor = newpin
                                        ##stringSent = 'The New Pin is ' + opendoor
                                        ## Sent Pin to the person's phone number
                                        my_rpi.publish("ush/keypad/pin", opendoor, 1)
                                        print("[+] Sending OTP to Email")
                    
                    while(GPIO.input(ROW[i]) == 0):
                        pass

            GPIO.output(COL[j],1)
except:
    GPIO.cleanup()