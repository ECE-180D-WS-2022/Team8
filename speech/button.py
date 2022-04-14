'''
Documentation for button press: https://raspberrypihq.com/use-a-push-button-with-raspberry-pi-gpio/
'''

import RPi.GPIO as GPIO	#import Pi GPIO library
import time
from time import sleep

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)	#Set pin 10 to be an input pin and set init. value to be pulled low (off)
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)	#Same for pin 11

length = 0
flag = 0
enter = 0


while True:
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
