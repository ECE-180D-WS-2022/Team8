ls
import pyaudio
import wave
import soundfile as sf
import paho.mqtt.client as mqtt
#import speech_recognition as sr

def on_connect(client, userdata, flags, rc):
        print("Connection returned result: "+str(rc))
# Subscribing in on_connect() means that if we lose the connection and
# reconnect then subscriptions will be renewed.
        client.subscribe("2Team8B", qos=2)
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


chunk = 1024	#record in c hunks of 1024 samples
sample_format = pyaudio.paInt16	#16 bits per sample
channels = 1
#fs = 44100	#record at 44100 samples/second
fs = 24000
seconds = 3
filename = 'test.wav'

p = pyaudio.PyAudio()	#Create interface to PortAudio

print('Recording')

stream = p.open(format = sample_format, channels = channels, rate = fs, frames_per_buffer = chunk, input = True)
frames = []	#Array to store frames
#Store data in chunks for 3 seconds
for i in range(0, int(fs/chunk*seconds)):
	data = stream.read(chunk)
	frames.append(data)

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

f = open("test.wav", "rb")
imagestring = f.read()
f.close()
byteArray = bytearray(imagestring)

mqttc.publish('2Team8A', byteArray)

client.loop_stop()
client.disconnect()
