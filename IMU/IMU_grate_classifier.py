'''
        Read Gyro and Accelerometer by Interfacing Raspberry Pi with MPU6050 using Python
	http://www.electronicwings.com
'''
import smbus2 as smbus			#import SMBus module of I2C
from time import sleep          #import
import time
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
counter =  0
Gz_arr = []
Gy_arr = []
Gx_arr = []
Az_arr = []
Ay_arr = []
Ax_arr = []
COUNTER_THRESH = 15

CHOP_SENSITIVITY_SCALING = 0
CHOP_THRESH = 0
GOOD_CHOP_THRESH = 2
DECENT_CHOP_THRESH = 4

for i in range(COUNTER_THRESH):
	Gz_arr.append(i)
	Gy_arr.append(i)
	Gx_arr.append(i)
	Az_arr.append(i)
	Ay_arr.append(i)
	Ax_arr.append(i)

def MPU_Init():	#initialize the IMU
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

def read_raw_data(addr):	#read data from IMU
	#Accelero and Gyro value are 16-bit
        high = bus.read_byte_data(Device_Address, addr)
        low = bus.read_byte_data(Device_Address, addr+1)
	    
        #concatenate higher and lower value
        value = ((high << 8) | low)
        
        #to get signed value from mpu6050
        if(value > 32768):
                value = value - 65536
        return value


bus = smbus.SMBus(1) 	# or bus = smbus.SMBus(0) for older version boards
time.sleep(1)
Device_Address = 0x68   # MPU6050 device address

MPU_Init()

print (" Reading Data of Gyroscope and Accelerometer")
#print (Gy_arr)
#print(Gz_arr)
while True:
	
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
	


	#print ("%.2f" %Gx+ " "+ "%.2f" %Gy +" "+ "%.2f" %Gz + " " + "%.2f" %Ax+ " " +  "%.2f" %Ay +" "+ "%.2f" %Az) 	
	#if (Gz >=0.15 or Gz <=-0.15):
		
		#print('it is either lifting or pushing')
		#if (Gy > 1 or Gy < -1):
			#print('pushing')
		#else:
			#print('lifting')
	#else:
		#print('still')
	#if abs(Gy) <= 0.6:
		#print('idle')
	#else:
		#print('not idle')

	#implement memory for key data points
	Gz_arr[counter] = Gz
	Gy_arr[counter] = Gy
	Gx_arr[counter] = Gx
	
	Az_arr[counter] = Az
	Ay_arr[counter] = Ay
	Ax_arr[counter] = Ax
	counter+=1
	
	if (counter == COUNTER_THRESH):
		'''
		max_Gz = max(Gz_arr)
		max_Gy = max(Gy_arr)
		max_Gx = max(Gx_arr)
		min_Gz = min(Gz_arr)
		min_Gy = min(Gy_arr)
		min_Gx = min(Gx_arr)

		max_Az = max(Az_arr)
		max_Ay = max(Ay_arr)
		max_Ax = max(Ax_arr)
		min_Az = min(Az_arr)
		min_Ay = min(Ay_arr)
		min_Ax = min(Ax_arr)
		'''
		avg_Gx = sum(Gx_arr) / len(Gx_arr)
		avg_Gy = sum(Gy_arr) / len(Gy_arr)
		avg_Gz = sum(Gz_arr) / len(Gz_arr)
		
		avg_Ax = sum(Ax_arr) / len(Ax_arr)
		avg_Ay = sum(Ay_arr) / len(Ay_arr)
		avg_Az = sum(Az_arr) / len(Az_arr)

		#Correct side currently pointing down
		if ((abs(Ax) > abs(Ay)-CHOP_SENSITIVITY_SCALING and abs(Ax) > abs(Az)-CHOP_SENSITIVITY_SCALING) or (abs(Ax) <= abs(Ay)+CHOP_SENSITIVITY_SCALING and abs(Ax) <= abs(Az)+CHOP_SENSITIVITY_SCALING and abs(Gz) > 3)):	
			#print('correct side down')
			if abs(avg_Gz) > (abs(avg_Gx)+CHOP_THRESH) and abs(avg_Gz) > (abs(avg_Gy)+CHOP_THRESH):	#chopping motion (up and down) detected
				#print('chop detected')
				if abs(avg_Gx) < GOOD_CHOP_THRESH and abs(avg_Gy) < GOOD_CHOP_THRESH:
					#print('good chopping')
					print('3')
				elif abs(avg_Gx) < DECENT_CHOP_THRESH and abs(avg_Gy) < DECENT_CHOP_THRESH:
					#print('decent chopping')
					print('2')
			else:
				#print ('meh chopping')
				print('1')
		else:
			print('idle')
		''' next steps: give feedback to the player
		elif abs(Gx) > abs(Gz) and abs(Gx) > abs(Gy):
			print('straighten your cut')
		elif abs(Gy) > abs(Gz) and abs(Gy) > abs(Gx):
			print("don't angle your blade")
		else:
			print('L')
		'''
		counter = 0
	
	#sleep(0.01)
