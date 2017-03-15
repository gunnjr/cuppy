'''
/*
 * Copyright 2010-2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 *  http://aws.amazon.com/apache2.0
 *
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */
 '''

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import sys
import logging
import time
import getopt
import RPi.GPIO as GPIO

# Setup GPIO for relay control
GPIO.setmode(GPIO.BCM)

# switching serially through 2 relays due to lack of confidence in hardware
inUsePinList = [2, 3]

# loop through extra relays to show we're up and running
unUsedPinList = [4, 17]
for i in unUsedPinList:
	GPIO.setup(i, GPIO.OUT)
	GPIO.output(i, GPIO.HIGH)
	time.sleep(1)
	GPIO.output(i, GPIO.LOW)
	time.sleep(1)
	GPIO.output(i, GPIO.HIGH)

# set mode and state to 'high' on our in-use pins
for i in inUsePinList:
	GPIO.setup(i, GPIO.OUT)
	GPIO.output(i, GPIO.HIGH)

# Custom MQTT message callback
def cbFill(client, userdata, message):
	print("cbFill: Received a new message. Payload folows on next line: ")
	print(message.payload)
	print("cbFill:from topic: ")
	print(message.topic)
	print("cbFill: now going to open relay for this many secs:" + str(message.payload))
	try:	
		for i in inUsePinList:
			GPIO.output(i, GPIO.LOW)
		
		time.sleep(float(message.payload))

		print "cbFill: Now closing."

		for i in inUsePinList:
			GPIO.output(i, GPIO.HIGH)

	# End program cleanly if there's an exception
	except:
	  # Reset GPIO settings
	  GPIO.cleanup()
	  raise	

# Custom MQTT message callback
def cbCloseValve(client, userdata, message):
	print("cbCloseValve: Received a new message. Payload folows on next line: ")
	print(message.payload)
	print("cbCloseValve:from topic: ")
	print(message.topic)
  	print("close the valve then sleep for a second")
	GPIO.output(relayPin, GPIO.HIGH)
	time.sleep(1)
	print("cbCloseValve: back from sleep")
	print("--------------\n\n")


# Usage
usageInfo = """Usage:

Use certificate based mutual authentication:
python basicPubSub.py -e <endpoint> -r <rootCAFilePath> -c <certFilePath> -k <privateKeyFilePath>

Use MQTT over WebSocket:
python basicPubSub.py -e <endpoint> -r <rootCAFilePath> -w

Type "python basicPubSub.py -h" for available options.
"""
# Help info
helpInfo = """-e, --endpoint
	Your AWS IoT custom endpoint
-r, --rootCA
	Root CA file path
-c, --cert
	Certificate file path
-k, --key
	Private key file path
-w, --websocket
	Use MQTT over WebSocket
-h, --help
	Help information


"""

# Read in command-line parameters
useWebsocket = False
host = ""
rootCAPath = ""
certificatePath = ""
privateKeyPath = ""
try:
	opts, args = getopt.getopt(sys.argv[1:], "hwe:k:c:r:", ["help", "endpoint=", "key=","cert=","rootCA=", "websocket"])
	if len(opts) == 0:
		raise getopt.GetoptError("No input parameters!")
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			print(helpInfo)
			exit(0)
		if opt in ("-e", "--endpoint"):
			host = arg
		if opt in ("-r", "--rootCA"):
			rootCAPath = arg
		if opt in ("-c", "--cert"):
			certificatePath = arg
		if opt in ("-k", "--key"):
			privateKeyPath = arg
		if opt in ("-w", "--websocket"):
			useWebsocket = True
except getopt.GetoptError:
	print(usageInfo)
	exit(1)

# Missing configuration notification
missingConfiguration = False
if not host:
	print("Missing '-e' or '--endpoint'")
	missingConfiguration = True
if not rootCAPath:
	print("Missing '-r' or '--rootCA'")
	missingConfiguration = True
if not useWebsocket:
	if not certificatePath:
		print("Missing '-c' or '--cert'")
		missingConfiguration = True
	if not privateKeyPath:
		print("Missing '-k' or '--key'")
		missingConfiguration = True
if missingConfiguration:
	exit(2)

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = None
if useWebsocket:
	myAWSIoTMQTTClient = AWSIoTMQTTClient("basicPubSub", useWebsocket=True)
	myAWSIoTMQTTClient.configureEndpoint(host, 443)
	myAWSIoTMQTTClient.configureCredentials(rootCAPath)
else:
	myAWSIoTMQTTClient = AWSIoTMQTTClient("basicPubSub")
	myAWSIoTMQTTClient.configureEndpoint(host, 8883)
	myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect()
myAWSIoTMQTTClient.subscribe("cuppy/fill", 1, cbFill)
myAWSIoTMQTTClient.subscribe("cuppy/closeValve", 1, cbCloseValve)
time.sleep(2)

# Publish to the same topic in a loop forever
loopCount = 0
while True:
	# print("ListenParent: Just sleeping and looping: " + str(loopCount))
	loopCount += 1
	try:	
		time.sleep(60)   
		for i in unUsedPinList:
			GPIO.output(i, GPIO.LOW)
			time.sleep(1)
			GPIO.output(i, GPIO.HIGH)	   
	# End program cleanly if there's an exception
	except:
	  # Reset GPIO settings
	  GPIO.cleanup()
	  raise	
