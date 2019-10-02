#!/usr/bin/python3

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)

#The BM will enter bootloader when XCK is pulled high to 2v and VCC is pulled high to 3.3v
#pin 16 = GPIO23
#pin 18 = GPIO24

#XCK pin to HIGH - need to reduce to 2v
GPIO.setup(16, GPIO.OUT, pull_up_down=GPIO.PUD_UP)
#VCC pin to HIGH
GPIO.setup(18, GPIO.OUT, pull_up_down=GPIO.PUD_UP)
