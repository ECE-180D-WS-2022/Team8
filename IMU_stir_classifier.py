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
Gx_arr = []
Gz_arr = []

G_THRESH = 1
COUNTER_THRESH = 15
TOP_SPEED_THRESH = 10
BOT_SPEED_THRESH = 2


for i in range(COUNTER_THRESH):
	Gz_arr.append(i)
	Gx_arr.append(i)

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

	#implement memory for key data points
	Gx_arr[counter]=Gx;
	Gz_arr[counter]=Gz;
	counter+=1
	
	if (counter == COUNTER_THRESH):
		max_Gx = max(Gx_arr)
		min_Gx = min(Gx_arr)

		max_Gz = max(Gz_arr)
		min_Gz = min(Gz_arr)
		if abs(Ay) > (0.75*G_THRESH) and abs(Ay) < (1.25*G_THRESH):	#pointing in the right direction within a certain threshold
			#print('pointing down')
			if (max_Gx - min_Gx) < TOP_SPEED_THRESH and (max_Gx - min_Gx) > BOT_SPEED_THRESH and (max_Gz - min_Gz) < TOP_SPEED_THRESH and (max_Gz - min_Gz) > BOT_SPEED_THRESH:	#good speed threshold, must maintain to score
				#print('Good speed')
				print('3')
			elif (max_Gx - min_Gx) >= TOP_SPEED_THRESH or (max_Gz - min_Gz) >= TOP_SPEED_THRESH:	#tell player to slow down
				print('slow down: 1')
			elif (max_Gx - min_Gx) <= BOT_SPEED_THRESH or (max_Gz - min_Gz) <= BOT_SPEED_THRESH:	#tell player to speed up
				print('speed up: 1')
			'''
			elif (max_Gx - min_Gx) < 10 and (max_Gx - min_Gx) > 2 and (max_Gz - min_Gz) < 10 and (max_Gz - min_Gz) > 2:
				print('Decent speed')
			else:
				print('Meh speed')
			'''
		else:
			print('not: 0')
		counter = 0
	#sleep(0.03)
