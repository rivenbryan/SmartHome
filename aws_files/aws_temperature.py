# Import SDK packages
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import time
from time import sleep,gmtime, strftime
import Adafruit_DHT
import json
import datetime as datetime
from rpi_lcd import LCD



pin = 26

# Custom MQTT message callback
def customCallback(client, userdata, message):
	print("Received a new message: ")
	print(message.payload)
	print("from topic: ")
	print(message.topic)
	print("--------------\n\n")
	
host = "abpl27ba00qyj-ats.iot.us-west-2.amazonaws.com"
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

print("-----------------------------------------------------------")
print("[+] Smart Home: Recording Temperature")


# Connect and subscribe to AWS IoT
my_rpi.connect()
my_rpi.subscribe("ush/sensors/temperature", 1, customCallback)
sleep(2)

lcd = LCD()

lcd.text('Smart Home v2 ', 1)
# Publish to the same topic in a loop forever
while True:

	message = {}

	humidity, temperature = Adafruit_DHT.read_retry(11, pin)
	print("[+] Temperature recorded " + str(temperature))
	now = datetime.datetime.now()
	
	lcd.text('Temperature :', 1)
	lcd.text(str(temperature), 2)
	time.sleep(2)
	
	message["deviceid"] = 'deviceID_bryan'
	message["datetimeid"] = now.isoformat()
	message["temperature"] =  temperature  
	my_rpi.publish("ush/sensors/temperature", json.dumps(message), 1)
	sleep(5)
