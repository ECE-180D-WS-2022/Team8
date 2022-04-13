'''
Documentation for button press: https://raspberrypihq.com/use-a-push-button-with-raspberry-pi-gpio/
'''

import RPi.GPIO as GPIO	#import Pi GPIO library
import time
from time import sleep

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)	#Set pin 7 to be an input pin and set init. value to be pulled low (off)

length = 0
flag = 0


while True:
	if GPIO.input(10) == GPIO.HIGH and flag == 0:
		flag = 1
	if flag == 1:
		print(length)
		length += 1
		sleep(2)
		flag = 0
