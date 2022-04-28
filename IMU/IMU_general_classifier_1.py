'''
        Read Gyro and Accelerometer by Interfacing Raspberry Pi with MPU6050 using Python
        http://www.electronicwings.com

	MQTT code obtained from ECE 180DA lab manual
'''

import smbus2 as smbus                  #import SMBus module of I2C
from time import sleep          #import
import time
import paho.mqtt.client as mqtt
import pyaudio
import wave
import soundfile as sf
import RPi.GPIO as GPIO	#import Pi GPIO library

#GLOBAL VARIABLES
op_status = '00'	#'00' means stop sending data, value != '00' need to send data to CPU
prev_score = 0
curr_score = 0

counter =  0
Gx_arr = []
Gz_arr = []
Gy_arr = []
Az_arr = []
Ay_arr = []
Ax_arr = []

Gx_roll_arr = []
Gz_roll_arr = []
Gy_roll_arr = []
Az_roll_arr = []
Ay_roll_arr = []
Ax_roll_arr = []

chunk = 1024	#record in c hunks of 1024 samples
sample_format = pyaudio.paInt16	#16 bits per sample
channels = 1
fs = 44100	#record at 44100 samples/second
seconds = 2
filename = 'test.wav'

speech_flag = 0	#0 means will setup speech channel, 1 means have already set it up
speech_recording_flag = 0	#0 means haven't recorded anything, 1 means recording waiting to be sent

#GLOBAL CONSTANTS
CHOP_SENSITIVITY_SCALING = 0
CHOP_THRESH = 2
GOOD_CHOP_THRESH = 2
DECENT_CHOP_THRESH = 4

G_THRESH = 1
COUNTER_THRESH = 20
TOP_STIR_SPEED_THRESH = 9
BOT_STIR_SPEED_THRESH = 3
DEC_TOP_STIR_SPEED_THRESH = 11
DEC_BOT_STIR_SPEED_THRESH = 1

ROLL_COUNTER_THRESH = 40	#more values taken because want to slow down movement of rolling
ROLL_SENSITIVITY_SCALING = 0
AY_ROLL_THRESH = 0.4		#avg_Ay must be smaller than this value
AZ_ROLL_THRESH_BOT = 0.2	#max - min Az must be larger than this value to register
AZ_ROLL_THRESH_TOP = 0.7	#max - min Az must be smaller than this value to register
GOOD_ROLL_THRESH = 1
DECENT_ROLL_THRESH = 4

total_Ax = 0
total_Az = 0
goal_Az = -100
goal_Ax_before = 100
goal_Ax_after = 30
pour_status_flag = 0    #0 means start pouring, 1 means in process of pouring, 2 means finished pouring, 3 means finished action


SAUTE_SENSITIVITY_SCALING = 0
SAUTE_THRESH = 1.5
GOOD_SAUTE_THRESH = 3
DECENT_SAUTE_THRESH = 8

# 0. define callbacks - functions that run when events happen.
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
	print("Connection returned result: "+str(rc))
# Subscribing in on_connect() means that if we lose the connection and
# reconnect then subscriptions will be renewed.
	client.subscribe("1Team8B", qos=2)
# The callback of the client when it disconnects.

def on_disconnect(client, userdata, rc):
	if rc != 0:
		print('Unexpected Disconnect')
	else:
		print('Expected Disconnect')

def on_message(client, userdata, message):	#receive operation command from CPU. -1 means stop, > 0 tells which action to classify
	global op_status

	temp = str(message.payload)	#message format: b'message'
	print('message')
	print(temp)
	op_status = str(temp[2:4])	#op_status will always be a string
	print('op_status')
	print(op_status)

#some MPU6050 Registers and their Address
PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
INT_ENABLE   = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H  = 0x43
GYRO_YOUT_H  = 0x45
GYRO_ZOUT_H  = 0x47


def MPU_Init():
        #write to sample rate register
	bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)
        
        #Write to power management register
	bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)
        
        #Write to Configuration register
	bus.write_byte_data(Device_Address, CONFIG, 0)
        
        #Write to Gyro configuration register
	bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)
        
        #Write to interrupt enable register
	bus.write_byte_data(Device_Address, INT_ENABLE, 1)

def read_raw_data(addr):
        #Accelero and Gyro value are 16-bit
	high = bus.read_byte_data(Device_Address, addr)
	low = bus.read_byte_data(Device_Address, addr+1)
            
        #concatenate higher and lower value
	value = ((high << 8) | low)
        
        #to get signed value from mpu6050
	if(value > 32768):
		value = value - 65536
	return value


bus = smbus.SMBus(1)    # or bus = smbus.SMBus(0) for older version boards
time.sleep(1)
Device_Address = 0x68   # MPU6050 device address

MPU_Init()

#Initialize push button
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
#GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)	#Set pin 10 to be an input pin and set init. value to be pulled low (off)
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)	#Same for pin 11

#connect to MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
client.connect_async("test.mosquitto.org")
client.loop_start()

for i in range(COUNTER_THRESH):
	Gz_arr.append(i)
	Gy_arr.append(i)
	Gx_arr.append(i)
	Az_arr.append(i)
	Ay_arr.append(i)
	Ax_arr.append(i)

for i in range(ROLL_COUNTER_THRESH):
	Gx_roll_arr.append(i)
	Gy_roll_arr.append(i)
	Gz_roll_arr.append(i)
	Ax_roll_arr.append(i)
	Ay_roll_arr.append(i)
	Az_roll_arr.append(i)


while True:	#continuously loop, even if don't need to collect data
	while GPIO.input(11) == GPIO.HIGH:
		if speech_flag == 0:	#setup audio collection channel 
			p = pyaudio.PyAudio()   #Create interface to PortAudio
			stream = p.open(format = sample_format, channels = channels, rate = fs, frames_per_buffer = chunk, input = True)
			frames = []	#Array to store frames
			speech_flag = 1
		data = stream.read(chunk, exception_on_overflow = False)
		frames.append(data)
		speech_recording_flag = 1
	if speech_recording_flag == 1:	#just finished recording data
		#stop and close stream
		stream.stop_stream()
		stream.close()
		#Terminate PortAudio interface
		p.terminate()

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
		client.publish('1Team8C', byteArray)
		speech_flag = 0	#reset speech flags after recording
		speech_recording_flag = 0
		print("wav sent")
	while op_status != '00':        #Perform operation set by op_status
		while GPIO.input(11) == GPIO.HIGH:
			if speech_flag == 0:    #setup audio collection channel 
				p = pyaudio.PyAudio()   #Create interface to PortAudio
				stream = p.open(format = sample_format, channels = channels, rate = fs, frames_per_buffer = chunk, input = True)
				frames = []     #Array to store frames
				speech_flag = 1
			data = stream.read(chunk, exception_on_overflow = False)
			frames.append(data)
			speech_recording_flag = 1
		if speech_recording_flag == 1:  #just finished recording data
                  	#stop and close stream
			stream.stop_stream()
			stream.close()
                        #Terminate PortAudio interface
			p.terminate()

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
			client.publish('1Team8C', byteArray)
			speech_flag = 0 #reset speech flags after recording
			speech_recording_flag = 0
			print("wav sent")
		#Read Accelerometer raw value
		acc_x = read_raw_data(ACCEL_XOUT_H)
		acc_y = read_raw_data(ACCEL_YOUT_H)
		acc_z = read_raw_data(ACCEL_ZOUT_H)
        
        	#Read Gyroscope raw value
		gyro_x = read_raw_data(GYRO_XOUT_H)
		gyro_y = read_raw_data(GYRO_YOUT_H)
		gyro_z = read_raw_data(GYRO_ZOUT_H)
        
        	#Full scale range +/- 250 degree/C as per sensitivity scale factor
		Ax = acc_x/16384.0
		Ay = acc_y/16384.0
		Az = acc_z/16384.0
        
		Gx = gyro_x/131.0
		Gy = gyro_y/131.0
		Gz = gyro_z/131.0
		
		if op_status == '02':	#chop and grate
			Gz_arr[counter] = Gz
			Gy_arr[counter] = Gy
			Gx_arr[counter] = Gx
			Az_arr[counter] = Az
			Ay_arr[counter] = Ay
			Ax_arr[counter] = Ax
			counter+=1

			if (counter == COUNTER_THRESH):
				avg_Gx = sum(Gx_arr) / len(Gx_arr)
				avg_Gy = sum(Gy_arr) / len(Gy_arr)
				avg_Gz = sum(Gz_arr) / len(Gz_arr)
				avg_Ax = sum(Ax_arr) / len(Ax_arr)
				avg_Ay = sum(Ay_arr) / len(Ay_arr)
				avg_Az = sum(Az_arr) / len(Az_arr)

				if ((abs(Ax) > abs(Ay)-CHOP_SENSITIVITY_SCALING and abs(Ax) > abs(Az)-CHOP_SENSITIVITY_SCALING) or (abs(Ax) <= abs(Ay)+CHOP_SENSITIVITY_SCALING and abs(Ax) <= abs(Az)+CHOP_SENSITIVITY_SCALING and abs(Gz) > 3)):
                			#print('correct side down')
					if abs(avg_Gz) > (abs(avg_Gx)+CHOP_THRESH) and abs(avg_Gz) > (abs(avg_Gy)+CHOP_THRESH): #chopping motion (up and down) detected
						if abs(avg_Gx) < GOOD_CHOP_THRESH and abs(avg_Gy) < GOOD_CHOP_THRESH:
                                			#print('good chopping')
							curr_score = 3
					elif abs(avg_Gx) < DECENT_CHOP_THRESH and abs(avg_Gy) < DECENT_CHOP_THRESH:
                                			#print('decent chopping')
							curr_score = 2
					else:	#guarantee that there will always be small progress as long as correct side pointing down
						#print ('meh chopping')
						curr_score = 1
				else:
					curr_score = 0
				counter = 0
		elif op_status == '03':	#stir
			Gx_arr[counter]=Gx;
			Gz_arr[counter]=Gz;
			counter+=1
			if (counter == COUNTER_THRESH):
				max_Gx = max(Gx_arr)
				min_Gx = min(Gx_arr)

				max_Gz = max(Gz_arr)
				min_Gz = min(Gz_arr)
				if abs(Ay) > (0.75*G_THRESH) and abs(Ay) < (1.25*G_THRESH):     #pointing in the right direction within a certain threshold
                        		#print('pointing down')
					#good speed threshold
					if (max_Gx - min_Gx) < TOP_STIR_SPEED_THRESH and (max_Gx - min_Gx) > BOT_STIR_SPEED_THRESH and (max_Gz - min_Gz) < TOP_STIR_SPEED_THRESH and (max_Gz - min_Gz) > BOT_STIR_SPEED_THRESH:     
						#print('Good speed')
						curr_score = 3
					elif (max_Gx - min_Gx) >= TOP_STIR_SPEED_THRESH or (max_Gz - min_Gz) >= TOP_STIR_SPEED_THRESH:    #tell player to slow down, return value of 2 for CPU to let player know to slow down
						#print('slow down: 1')
						curr_score = 2
					elif (max_Gx - min_Gx) <= BOT_STIR_SPEED_THRESH or (max_Gz - min_Gz) <= BOT_STIR_SPEED_THRESH:    #tell player to speed up, return value of 1 for CPU to let player know to speed up
						#print('speed up: 1')
						curr_score = 1
				else:
					curr_score = 0
					'''
					#decent speed threshold
					elif (max_Gx - min_Gx) < DEC_TOP_STIR_SPEED_THRESH and (max_Gx - min_Gx) > DEC_BOT_STIR_SPEED_THRESH and (max_Gz - min_Gz) < DEC_TOP_STIR_SPEED_THRESH and (max_Gz - min_Gz) > DEC_BOT_STIR_SPEED_THRESH:
						curr_score = 2
					else:
						curr_score = 1
					'''
				counter = 0	#reset counter after operation with memory
		elif op_status == '04':	#roll and garnish
			Gz_roll_arr[counter] = Gz
			Gy_roll_arr[counter] = Gy
			Gx_roll_arr[counter] = Gx
			Az_roll_arr[counter] = Az
			Ay_roll_arr[counter] = Ay
			Ax_roll_arr[counter] = Ax
			counter+=1
			if (counter == ROLL_COUNTER_THRESH):
				max_Gz = max(Gz_roll_arr)
				max_Gy = max(Gy_roll_arr)
				max_Gx = max(Gx_roll_arr)
				min_Gz = min(Gz_roll_arr)
				min_Gy = min(Gy_roll_arr)
				min_Gx = min(Gx_roll_arr)

				max_Az = max(Az_roll_arr)
				max_Ay = max(Ay_roll_arr)
				max_Ax = max(Ax_roll_arr)
				min_Az = min(Az_roll_arr)
				min_Ay = min(Ay_roll_arr)
				min_Ax = min(Ax_roll_arr)

				avg_Gx = sum(Gx_roll_arr) / len(Gx_roll_arr)
				avg_Gy = sum(Gy_roll_arr) / len(Gy_roll_arr)
				avg_Gz = sum(Gz_roll_arr) / len(Gz_roll_arr)
	
				avg_Ax = sum(Ax_roll_arr) / len(Ax_roll_arr)
				avg_Ay = sum(Ay_roll_arr) / len(Ay_roll_arr)
				avg_Az = sum(Az_roll_arr) / len(Az_roll_arr)

				#Correct side currently pointing down
				if ((abs(Ax) > abs(Ay)-ROLL_SENSITIVITY_SCALING and abs(Ax) > abs(Az)-ROLL_SENSITIVITY_SCALING) or (abs(Ax) <= abs(Ay)+ROLL_SENSITIVITY_SCALING and abs(Ax) <= abs(Az)+ROLL_SENSITIVITY_SCALING and abs(Gz) > 3)):
				#print('correct side down')
					if (max_Az - min_Az) > AZ_ROLL_THRESH_BOT and (max_Az - min_Az) < AZ_ROLL_THRESH_TOP and avg_Ay < AY_ROLL_THRESH:
					#print('rolling')
						if avg_Gx < GOOD_ROLL_THRESH and avg_Gy < GOOD_ROLL_THRESH and avg_Gz < GOOD_ROLL_THRESH:
							curr_score = 3
						elif avg_Gx < DECENT_ROLL_THRESH and avg_Gy < DECENT_ROLL_THRESH and avg_Gz < DECENT_ROLL_THRESH:
							curr_score = 2
					else:
						curr_score = 1
				counter = 0
		elif op_status == '05':	#pour
			if (pour_status_flag == 0):	#before start pouring, setup
				if (Ax < 1.3 and Ax > 0.99):	#Ax correctly facing down
					curr_score = 0	#for pour, return 0 when finished with setup stage
					total_Ax = total_Ax + Ax
			elif (pour_status_flag == 1):
				if (Az > -1 and Az < -0.8):	#-Az correctly facing down
					curr_score = 1	#return 1 when finished with stage 1
					total_Az = total_Az + Az
			elif (pour_status_flag == 2):
				if (Ax < 1.3 and Ax > 0.99):	#Ax returned to original position
					curr_score = 2	#return 2 when finished with stage 2
					total_Ax = total_Ax + Ax

			if (total_Ax >= goal_Ax_before and pour_status_flag == 0):	#start actual pouring process
				#print('stat 1')
				pour_status_flag = 1
			elif (total_Az <= goal_Az and pour_status_flag == 1):	#finish up actual pouring process
				#print('stat 2')
				pour_status_flag = 2
				total_Ax = 0
			elif (total_Ax >= goal_Ax_after and pour_status_flag == 2):	#finish up motion
				curr_score = 3	#return 3 when action completely finished
		elif op_status == '06': #saute
			Gz_roll_arr[counter] = Gz
			Gy_roll_arr[counter] = Gy
			Gx_roll_arr[counter] = Gx
			Az_roll_arr[counter] = Az
			Ay_roll_arr[counter] = Ay
			Ax_roll_arr[counter] = Ax
			counter += 1
			if counter == ROLL_COUNTER_THRESH:	#same speed of return as roll function
				max_Az = max(Az_roll_arr)
				max_Ay = max(Ay_roll_arr)
				max_Ax = max(Ax_roll_arr)
				min_Az = min(Az_roll_arr)
				min_Ay = min(Ay_roll_arr)
				min_Ax = min(Ax_roll_arr)

				avg_Gx = sum(Gx_roll_arr) / len(Gx_roll_arr)
				avg_Gy = sum(Gy_roll_arr) / len(Gy_roll_arr)
				avg_Gz = sum(Gz_roll_arr) / len(Gz_roll_arr)
        
				avg_Ax = sum(Ax_roll_arr) / len(Ax_roll_arr)
				avg_Ay = sum(Ay_roll_arr) / len(Ay_roll_arr)
				avg_Az = sum(Az_roll_arr) / len(Az_roll_arr)
				if abs(Az) > abs(Ax)-SAUTE_SENSITIVITY_SCALING and abs(Az) > abs(Ay)-SAUTE_SENSITIVITY_SCALING:	
					#print('correct side down')
					if abs(max_Ay) + abs(min_Ay) > SAUTE_THRESH and avg_Az > 1.1 and avg_Az < 1.3:
						#print('saute detected')
						if abs(avg_Gy) < GOOD_SAUTE_THRESH and abs(avg_Gz) < GOOD_SAUTE_THRESH:
							#print('good chopping')
							curr_score = 3
						elif abs(avg_Gy) < DECENT_SAUTE_THRESH and abs(avg_Gz) < DECENT_SAUTE_THRESH:
							#print('decent chopping')
							curr_score = 2
					else:
						#print ('meh chopping')
						curr_score = 1
				counter = 0
		if prev_score != curr_score:	#when see a new score, send update to CPU
			prev_score = curr_score
			message = op_status + str(curr_score)	#format: "023" means chopping (02) got a return score of 3
			print(message)
			client.publish('1Team8A', message, qos=2)
			sleep(1)
        #reset score variables when done with each operation
	prev_score = 0
	curr_score = 0
	counter = 0

#Disconnect MQTT
client.loop_stop()
client.disconnect()
