"""
	EE250 Final Project
	VM Publisher Code
	
	github repo:
	Group Members: Chris Manna, Sara Lim, Hannah Rose
"""
import paho.mqtt.client as mqtt
import time
import sounddevice as sd
from scipy.io.wavfile import write
from pydub import AudioSegment
from ShazamAPI import Shazam
import json
import matplotlib.pyplot as plt
import numpy as np


#no subscritptions, just connect to server
def on_connect(client, userdata, flags, rc):
	print("Connected to server (i.e., broker) with result code "+str(rc))


#Default message callback. Please use custom callbacks.
def on_message(client, userdata, msg):
	print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))


#recognize song from mp3 and publish for RPI
def Shzm(mp3):
	mp3_file_content_to_recognize = open(mp3, 'rb').read()
	shazam = Shazam(mp3_file_content_to_recognize)
	recognize_generator = shazam.recognizeSong()
	songJSON = (next(recognize_generator))[1]
	print("test")
	try: 
		Title = "Title: "+ songJSON["track"]["title"]
		Artist = "Artist: " + songJSON["track"]["subtitle"]
		client.publish("audIOT/SHAZAM", Title + "\n" + Artist)
	except:
		#print("cannot find song")
		client.publish("audIOT/SHAZAM","Song Not Detected")


#records computer microphone and saves as mp3	
def microphone():
	fs = 44100 #sample rate
	seconds = 7 #duration
	myrecording = sd.rec(int(seconds *fs), samplerate = fs, channels = 2)
	sd.wait()
	write('t.wav', fs, myrecording)
	sound = AudioSegment.from_wav('t.wav')
	sound.export('song.mp3', format = 'mp3')
	Shzm('song.mp3')

#converts microphone audio to FFT to adjust light of LED on RPI
def FFT():
	i = 0 #TO DO incorperate FFT page
	
	#client.publish("audIOT/FFT", #publish frequency stuff for LED



if __name__ == '__main__':
	#this section is covered in publisher_and_subscriber_example.py
	client = mqtt.Client()
	client.on_message = on_message
	client.on_connect = on_connect
	client.connect(host="eclipse.usc.edu", port=11000, keepalive=60)
	client.loop_start()

	while True:
		microphone()
		##transmit frequency to pi
    	
		##transmit song name to pi
		time.sleep(1)
            

