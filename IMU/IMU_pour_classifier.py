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
total_Ax = 0
total_Az = 0
goal_Az = -100
goal_Ax_before = 100
goal_Ax_after = 30
COUNTER_THRESH = 15
pour_status_flag = 0	#0 means start pouring, 1 means in process of pouring, 2 means finished pouring, 3 means finished action

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

	#implement memory for key data points
	
	if (pour_status_flag == 0):	#before start pouring, setup
		if (Ax < 1.3 and Ax > 0.99):	#Ax correctly facing down
			print('0')
			total_Ax = total_Ax + Ax
	elif (pour_status_flag == 1):
		if (Az > -1 and Az < -0.8):	#-Az correctly facing down
			print('1')
			total_Az = total_Az + Az
	elif (pour_status_flag == 2):
		if (Ax < 1.3 and Ax > 0.99):	#Ax returned to original position
			print('2')
			total_Ax = total_Ax + Ax

	if (total_Ax >= goal_Ax_before and pour_status_flag == 0):	#start actual pouring process
		print('stat 1')
		pour_status_flag = 1
	elif (total_Az <= goal_Az and pour_status_flag == 1):	#finish up actual pouring process
		print('stat 2')
		pour_status_flag = 2
		total_Ax = 0
	elif (total_Ax >= goal_Ax_after and pour_status_flag == 2):	#finish up motion
		print('finished')
		break
