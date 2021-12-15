#!/usr/bin/env python
#########################################################
#   File name: LED_SWITCH.py
#      Author: ZDZ
#        Date: 2019/01/23
#########################################################
import RPi.GPIO as GPIO
import time

speed_Pin = 22      # 光电开关信号接在pin22, GPIO_GEN6
led_Pin = 11        # LED接在pin11, GPIO_GEN0
ledStatus = True    # 设定LED状态
edge_time = 0

def setup():
    GPIO.setwarnings(False)
    #GPIO.setmode(GPIO.BCM)
    GPIO.setmode(GPIO.BOARD)    # Numbers GPIOs by physical location
    GPIO.setup(speed_Pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)   # Set pin's mode is intput
    GPIO.setup(led_Pin, GPIO.OUT)
    GPIO.add_event_detect(speed_Pin, edge=GPIO.BOTH, callback=my_callback)


def my_callback(speed_Pin):
    global edge_time
    if (edge_time == 0):
        print("edge_RISING!")
        edge_time += 1
    else:
        print("edge_FALLING!")
        edge_time = 0
    global ledStatus
    if (edge_time == 1):
        ledStatus = not ledStatus
    else:
        pass

def loop():
    print("test beginning...")
    while True:
        if ledStatus:
            GPIO.output(led_Pin, GPIO.HIGH)
        else:
            GPIO.output(led_Pin, GPIO.LOW)

def destroy():
    GPIO.cleanup()  # Release resource


if __name__ == '__main__':  # Program start from here
    setup()
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child function destroy() will be  executed.
        print("stop...")
        destroy()
