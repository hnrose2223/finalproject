"""
	EE250 Final Project
	RPI Subscriber Code
	
	github repo:
	Group Members: Chris Manna, Sara Lim, Hannah Rose
"""
import paho.mqtt.client as mqtt
import time
import grovepi
from grovepi import *
from grove_rgb_lcd import *

#sets up LED
def gpi_setup():
    
    #UPDATE
    """
    #led setup
    global PORT_LED
    PORT_LED = 2   # D2 ~ port for LED
    pinMode(PORT_LED, "OUTPUT")
    digitalWrite(PORT_LED, 0)
    """

#LED subscription based on song frequency
def LED(client, userdata, message):
    #TO DO
    i = 0
    

#prints Song name and Title on PI LCD screen
def LCD(client, usedata, message):
    display_string = (str(message.payload, "utf-8"))
    if(display_string = "No Song \nDetected"):
    	setRGB(64,0,0)
    else:
    	setRGB(0,65,65)
    setText(display_string)
    #print(display_string)


#subscribe to topics here
def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code "+str(rc))

    #subscribe to topics of interest here
    client.subscribe("audIOT/FFT")
    client.message_callback_add("audIOT/FFT", LED)
    
    client.subscribe("audIOT/SHAZAM")
    client.message_callback_add("audIOT/SHAZAM", LCD)

#Default message callback. Please use custom callbacks.
def on_message(client, userdata, msg):
    print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))

if __name__ == '__main__':
    #this section is covered in publisher_and_subscriber_example.py
    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(host="eclipse.usc.edu", port=11000, keepalive=60)
    client.loop_start()
    gpi_setup()
    while True:
        time.sleep(1)
