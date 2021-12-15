#!/usr/bin/env python
#########################################################
#   File name: Slot_photoelectric_switch.py
#      Author: ZDZ
#        Date: 2019/01/21
#########################################################
import RPi.GPIO as GPIO
import time

speed_Pin = 22   # 光电开关信号接在pin16,GPIO_GEN4
led_Pin = 11
ledStatus = True

def setup():
    GPIO.setwarnings(False)
    #GPIO.setmode(GPIO.BCM)
    GPIO.setmode(GPIO.BOARD)    # Numbers GPIOs by physical location
    GPIO.setup(speed_Pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)   # Set pin's mode is intput
    GPIO.setup(led_Pin, GPIO.OUT)

def my_callback(channel):
    print("button pressed!")
    global ledStatus
    ledStatus = not ledStatus
    if ledStatus:
        GPIO.output(led_Pin, GPIO.HIGH)
        pass
    else:
        GPIO.output(led_Pin, GPIO.LOW)
        pass
    pass


def loop():
    GPIO.add_event_detect(speed_Pin, GPIO.RISING, callback=my_callback, bouncetime=200)
    cnt_Value = 0
    print("test...")
    while True:
        input_value = GPIO.input(speed_Pin)
        if input_value == True:
            cnt_Value += 1
            print("The button has been pressed.", cnt_Value)
            while input_value == True:
                input_value = GPIO.input(speed_Pin)

def destroy():
    GPIO.cleanup()  # Release resource


if __name__ == '__main__':  # Program start from here
    setup()
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child function destroy() will be  executed.
        print("stop...")
        destroy()
