'''
        Read Gyro and Accelerometer by Interfacing Raspberry Pi with MPU6050 using Python
        http://www.electronicwings.com

	MQTT code obtained from ECE 180DA lab manual
'''

import smbus2 as smbus                  #import SMBus module of I2C
from time import sleep          #import
import time
import paho.mqtt.client as mqtt

#GLOBAL VARIABLES
op_status = '00'	#'00' means stop sending data, value != '00' need to send data.'02' means chop, '03' means stir
prev_score = 0
curr_score = 0

counter =  0
Gx_arr = []
Gz_arr = []
Gy_arr = []

Az_arr = []
Ay_arr = []
Ax_arr = []

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

# 0. define callbacks - functions that run when events happen.
# The callback for when the client receives a CONNACK response from the server.
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

while True:	#continuously loop, even if don't need to collect data
	while op_status != '00':        #runs when op_status != -1. Perform operation set by op_status
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
		
		if op_status == '02':	#chop
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

		if prev_score != curr_score:	#when see a new score, send update to CPU
			prev_score = curr_score
			message = op_status + str(curr_score)	#format: "023" means chopping (02) got a return score of 3
			print(message)
			client.publish('2Team8A', message, qos=2)
			sleep(1)
        #reset score variables when done with each operation
	prev_score = 0
	curr_score = 0
	counter = 0

#Disconnect MQTT
client.loop_stop()
client.disconnect()
