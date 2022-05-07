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
	global song_state
	mp3_file_content_to_recognize = open(mp3, 'rb').read()
	shazam = Shazam(mp3_file_content_to_recognize)
	recognize_generator = shazam.recognizeSong()
	songJSON = (next(recognize_generator))[1]
	print("test")
	try: 
		Title = songJSON["track"]["title"]
		Artist = songJSON["track"]["subtitle"]
		client.publish("audIOT/SHAZAM", Title + "\n" + Artist)
		client.publish("audIOT/FFT","LED_ON")
		song_state = 1
	except:
		#print("cannot find song")
		client.publish("audIOT/SHAZAM","No Song \nDetected")
		client.publish("audIOT/FFT","LED_OFF")
		song_state = 0


#records computer microphone and saves as mp3	
def microphone():
	global song_state
	if(song_state == 1):
		fs = 44100 #sample rate
		seconds = 1 #duration
		myrecording = sd.rec(int(seconds *fs), samplerate = fs, channels = 2)
		sd.wait()
		write('t.wav', fs, myrecording)
		sound = AudioSegment.from_wav('t.wav')
		sound.export('song.mp3', format = 'mp3')
		FFT('song.mp3')
	else:
		fs = 44100 #sample rate
		seconds = 5 #duration
		myrecording = sd.rec(int(seconds *fs), samplerate = fs, channels = 2)
		sd.wait()
		write('t.wav', fs, myrecording)
		sound = AudioSegment.from_wav('t.wav')
		sound.export('song.mp3', format = 'mp3')
		Shzm('song.mp3')
	

def get_max_frq(frq, fft):
	max_frq = 0
	max_fft = 0
	for idx in range(len(fft)):
		if abs(fft[idx]) > max_fft:
			max_fft = abs(fft[idx])
		max_frq = frq[idx]
	return max_frq
def get_peak_frqs(frq, fft):
    	
	low_frq = frq[0:150]
	high_frq = frq[150:299]
    
	low_frq_fft = fft[0:150]
	high_frq_fft = fft[150:299]

	return (get_max_frq(low_frq, low_frq_fft), get_max_frq(high_frq, high_frq_fft))


#converts microphone audio to FFT to adjust light of LED on RPI
def FFT(mp3):

	SLICE_SIZE = 1
	MAX_FRQ = 2000
	WINDOW_SIZE = 1 
	#client.publish("audIOT/FFT", #publish frequency stuff for LED
	print("Importing {}".format(mp3)) # file is the mp3 file
	audio = AudioSegment.from_mp3(mp3)

	sample_count = audio.frame_count()
	sample_rate = audio.frame_rate
	samples = audio.get_array_of_samples()
	period = 1/sample_rate                     #the period of each sample

	slice_sample_size = int(SLICE_SIZE*sample_rate)   #get the number of elements expected for [SLICE_SIZE] seconds

	n = slice_sample_size                            #n is the number of elements in the slice

   	#generating the frequency spectrum
	k = np.arange(n)                                #k is an array from 0 to [n] with a step of 1
	slice_duration = n/sample_rate                   #slice_duration is the length of time the sample slice is (seconds)
	frq = k/slice_duration                          #generate the frequencies by dividing every element of k by slice_duration
    
	max_frq_idx = int(MAX_FRQ*slice_duration)       #get the index of the maximum frequency (2000)
	frq = frq[range(max_frq_idx)]                   #truncate the frequency array so it goes from 0 to 2000 Hz
    
	start_index = 0                                 #set the starting index at 0
	end_index = start_index + slice_sample_size      #find the ending index for the slice
	output = ''
   
	print()
	i = 1
   	 
	while end_index < len(samples):
        
        	#print("Sample {}:".format(i))
		i += 1
    
       		#TODO: grab the sample slice and perform FFT on it
		sample_slice = samples[start_index: end_index]
		sample_slice_fft = np.fft.fft(sample_slice)/n   #perform fourier transform on sample_slice & normalize by n
        
        	#TODO: truncate the FFT to 0 to 2000 Hz
		fft = sample_slice_fft[range(max_frq_idx)]
        
        	#TODO: calculate the locations of the upper and lower FFT peak using get_peak_frqs()
		lower_peak,upper_peak = get_peak_frqs(frq,fft)
		print("lower: ", lower_peak)
		print("higheer: ",upper_peak)
        
		if (lower_peak < 40): # determine a value to separate high frequencies from low frequencies and blink an LED
           	 #print("right LED")
            		#digitalWrite(led_right,1)		# Send HIGH to switch on LED
			client.publish("audIOT/FFT","RLED_ON")
            		#time.sleep(0.1)
            		#digitalWrite(led_right,0)
		else:
            		client.publish("audIOT/FFT","RLED_OFF")
            
		if (upper_peak > 200):
           	 #print("left LED")
            		#digitalWrite(led_left,1)		# Send HIGH to switch on LED
			client.publish("audIOT/FFT","LLED_ON")
            		#time.sleep(0.1)
            		#digitalWrite(led_left,0)
		else:
            		client.publsih("audIOT/FFT","LLED_OFF")
        
        	#Incrementing the start and end window for FFT analysis
		start_index += int(WINDOW_SIZE*sample_rate)
		end_index = start_index + slice_sample_size

	print("Program completed")
	print("Decoded input: " + str(output))

if __name__ == '__main__':
	#this section is covered in publisher_and_subscriber_example.py
	client = mqtt.Client()
	client.on_message = on_message
	client.on_connect = on_connect
	client.connect(host="eclipse.usc.edu", port=11000, keepalive=60)
	client.loop_start()
	global song_state
	song_state = 0
	while True:
		microphone()
		##transmit frequency to pi
    	
		##transmit song name to pi
		time.sleep(.1)
            

