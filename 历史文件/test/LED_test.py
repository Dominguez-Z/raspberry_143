#!/usr/bin/env python
#########################################################
#   File name: LED_test.py
#      Author: ZDZ
#        Date: 2019/01/15
#########################################################
import RPi.GPIO as GPIO
import time

Long_LED = 11   # 远光LED接在pin11
Short_LED = 12  # 近光LED接在pin12
OPEN = 0
CLOSE = 1
def setup():
    GPIO.setwarnings(False)
    #GPIO.setmode(GPIO.BCM)
    GPIO.setmode(GPIO.BOARD)    # Numbers GPIOs by physical location
    GPIO.setup(Long_LED, GPIO.OUT)   # Set pin's mode is output
    GPIO.setup(Short_LED, GPIO.OUT)
    GPIO.output(Long_LED, CLOSE)
    GPIO.output(Short_LED, CLOSE)
def loop():
    print("twinkle...")
    while True:
        GPIO.output(Long_LED, CLOSE)
        GPIO.output(Short_LED, OPEN)
        time.sleep(1)
        GPIO.output(Long_LED, OPEN)
        GPIO.output(Short_LED, CLOSE)
        time.sleep(1)

def destroy():
    GPIO.output(Long_LED, False)
    GPIO.output(Short_LED, False)
    GPIO.cleanup()  # Release resource


if __name__ == '__main__':  # Program start from here
    setup()
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child function destroy() will be  executed.
        print("stop...")
        destroy()
