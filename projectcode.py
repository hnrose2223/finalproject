# Hannah Rose, Sara Lim, Chris Manna

import requests
import sys
import time
import numpy as np
from pydub import AudioSegment
import os

MAX_FRQ = 2000
SLICE_SIZE = 1 #??
WINDOW_SIZE = 1 #seconds?

sys.path.append('../../Software/Python/')
sys.path.append('../../Software/Python/grove_rgb_lcd')
sys.path.append('/home/pi/Dexter/GrovePi/Software/Python')

import grovepi
import grove_rgb_lcd as lcd

from grovepi import *

# Connect one of the Grove LED to digital port D4
# Connect another Grove LED to digital port D3
led_right = 4
led_left = 3

pinMode(led_right,"OUTPUT")
time.sleep(1)

pinMode(led_left,"OUTPUT")
time.sleep(1)

lcd.setRGB(128, 0, 0)

#from ShazamAPI import Shazam

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

def main(file): # we need to be able to load mp3 file from shazam (?)
    
    print("Importing {}".format(file))
    audio = AudioSegment.from_mp3(file)

    sample_count = audio.frame_count()
    sample_rate = audio.frame_rate
    samples = audio.get_array_of_samples()

    print("Number of channels: " + str(audio.channels))
    print("Sample count: " + str(sample_count))
    print("Sample rate: " + str(sample_rate))
    print("Sample width: " + str(audio.sample_width))

    period = 1/sample_rate                     #the period of each sample
    duration = sample_count/sample_rate         #length of full audio in seconds
    print("Duration:"+str(duration))

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
            digitalWrite(led_right,1)		# Send HIGH to switch on LED
            time.sleep(0.1)
            digitalWrite(led_right,0)
            
        if (upper_peak > 200):
            #print("left LED")
            digitalWrite(led_left,1)		# Send HIGH to switch on LED
            time.sleep(0.1)
            digitalWrite(led_left,0)
        
        #Incrementing the start and end window for FFT analysis
        start_index += int(WINDOW_SIZE*sample_rate)
        end_index = start_index + slice_sample_size

    print("Program completed")
    print("Decoded input: " + str(output))
        
if __name__ == '__main__':
    if len(sys.argv) != 2 or not os.path.isfile(sys.argv[1]):
        print("Usage: decode.py [file]")
        exit(1)
    main(sys.argv[1])
