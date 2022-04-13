'''
Documentation for button press: https://raspberrypihq.com/use-a-push-button-with-raspberry-pi-gpio/
'''

import RPi.GPIO as GPIO	#import Pi GPIO library

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)	#Set pin 7 to be an input pin and set init. value to be pulled low (off)

length = 0

while True:
	while GPIO.input(10) == GPIO.HIGH:
		print(length)
		length += 1
	length = 0
