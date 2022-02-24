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
#counter =  0
Gy_arr = []
Gz_arr = []

CHOP_SENSITIVITY_SCALING = 0.05
CHOP_THRESH = 2
GOOD_CHOP_THRESH = 2
DECENT_CHOP_THRESH = 4

for i in range(20):
	Gz_arr.append(i)
	Gy_arr.append(i)

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
	#Gy_arr[counter]=Gy;
	#Gz_arr[counter]=Gz;
	#print(counter)
	#counter+=1
	
	#if (counter == 20):
		#max_Gz = max(Gz_arr)
		#max_Gy = max(Gy_arr)
	if ((abs(Ax) > abs(Ay)-CHOP_SENSITIVITY_SCALING and abs(Ax) > abs(Az)-CHOP_SENSITIVITY_SCALING) or (abs(Ax) <= abs(Ay)+CHOP_SENSITIVITY_SCALING and abs(Ax) <= abs(Az)+CHOP_SENSITIVITY_SCALING and abs(Gz) > 3)):	#Correct side pointing down
		#print('correct side down')
		if abs(Gz) > (abs(Gx)+CHOP_THRESH) and abs(Gz) > (abs(Gy)+CHOP_THRESH):	#chopping motion (up and down) detected
			if abs(Gx) < GOOD_CHOP_THRESH and abs(Gy) < GOOD_CHOP_THRESH:
				#print('good chopping')
				print('3')
			elif abs(Gx) < DECENT_CHOP_THRESH and abs(Gy) < DECENT_CHOP_THRESH:
				#print('decent chopping')
				print('2')
		else:	
			#print ('meh chopping')
			print('1')
		
		'''
		elif abs(Gx) > abs(Gz) and abs(Gx) > abs(Gy):
			print('straighten your cut')
		elif abs(Gy) > abs(Gz) and abs(Gy) > abs(Gx):
			print("don't angle your blade")
		else:
			print('L')
		'''
	else:
		print('idle')	#for chopping classifier, nothing else matters
		'''
		if abs(Gx) <= 0.5 and abs(Gy) <= 0.5 and abs(Gz) <= 2.25:
			print('idle')
		elif  max_Gy > max_Gz:
			print('stirring')
		else:
			print('chopping')

		'''
		#counter = 0
		
	sleep(0.01)
