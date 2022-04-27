'''
Documentation for button press: https://raspberrypihq.com/use-a-push-button-with-raspberry-pi-gpio/
'''

import RPi.GPIO as GPIO	#import Pi GPIO library
import time
from time import sleep
import pyaudio
import wave
import soundfile as sf
import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, rc):
        print("Connection returned result: "+str(rc))
# Subscribing in on_connect() means that if we lose the connection and
# reconnect then subscriptions will be renewed.
        client.subscribe("3Team8B", qos=2)
# The callback of the client when it disconnects.

def on_disconnect(client, userdata, rc):
        if rc != 0:
                print('Unexpected Disconnect')
        else:
                print('Expected Disconnect')

def on_message(client, userdata, message):
        print('Received message')

# 1. create a client instance.
client = mqtt.Client()
# add additional client options (security, certifications, etc.)
# many default options should be good to start off.
# add callbacks to client.
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message

# 2. connect to a broker using one of the connect*() functions.
client.connect_async("test.mosquitto.org")
# 3. call one of the loop*() functions to maintain network traffic flow with the broker.
client.loop_start()

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)	#Set pin 10 to be an input pin and set init. value to be pulled low (off)
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)	#Same for pin 11

chunk = 1024    #record in c hunks of 1024 samples
sample_format = pyaudio.paInt16 #16 bits per sample
channels = 1
fs = 44100      #record at 44100 samples/second
seconds = 3
filename = 'test.wav'

p = pyaudio.PyAudio()   #Create interface to PortAudio

print('Recording')

stream = p.open(format = sample_format, channels = channels, rate = fs, frames_per_buffer = chunk, input = True)
frames = []     #Array to store frames


length = 0
flag = 0
enter = 0


while True:
	while GPIO.input(11) == GPIO.HIGH:
		data = stream.read(chunk, exception_on_overflow = False)
		frames.append(data)
		flag = 1
	if flag == 1:
		print('break')
		break
	'''
	if GPIO.input(11) == GPIO.HIGH and enter == 0:
		enter = 1
		print('entered station')
	while enter == 1:
		if GPIO.input(10) == GPIO.HIGH and flag == 0:
			flag = 1
		if flag == 1:
			print(length)
			length += 1
			sleep(2)
			flag = 0
			enter = 0
	'''
'''
chunk = 1024    #record in c hunks of 1024 samples
sample_format = pyaudio.paInt16 #16 bits per sample
channels = 1
fs = 44100      #record at 44100 samples/second
#fs = 24000
#fs = 8000
seconds = 3
filename = 'test.wav'

p = pyaudio.PyAudio()   #Create interface to PortAudio

print('Recording')

stream = p.open(format = sample_format, channels = channels, rate = fs, frames_per_buffer = chunk, input = True)
frames = []     #Array to store frames
#Store data in chunks for 3 seconds
for i in range(0, int(fs/chunk*seconds)):
        data = stream.read(chunk, exception_on_overflow = False)
        frames.append(data)
'''


#stop and close stream
stream.stop_stream()
stream.close()
#Terminate PortAudio interface
p.terminate()

print('Finished recording')

wf = wave.open(filename, 'wb')
wf.setnchannels(channels)
wf.setsampwidth(p.get_sample_size(sample_format))
wf.setframerate(fs)
wf.writeframes(b''.join(frames))
wf.close()

#playsound('test.wav')  #listen to what was just recorded for testing

f = open("test.wav", "rb")
imagestring = f.read()
f.close()
byteArray = bytearray(imagestring)

client.publish('3Team8A', byteArray)

client.loop_stop()
client.disconnect()

