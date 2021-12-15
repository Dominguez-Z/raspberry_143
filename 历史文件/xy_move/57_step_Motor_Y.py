#!/usr/bin/env python
#########################################################
#   File name: 57_step_Motor_Y.py
#      Author: ZDZ
#        Date: 2019/06/17
#########################################################
import RPi.GPIO as GPIO
import time

PUL = 11  # pin11
DIR = 13
us = 0.000001   # 微秒的乘数
ms = 0.001      # 毫秒的乘数


def one_step(step_number):                # time.sleep的参数最小为0.000001，但是宽度为60到80us不等。
    for i in range(0, step_number) :      # step_number为脉冲数
        time.sleep(100*us)
        GPIO.output(PUL, False)
        time.sleep(100*us)
        GPIO.output(PUL, True)

def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)    # Numbers GPIOs by physical location
    GPIO.setup(PUL, GPIO.OUT)   # Set pin's mode is output
    GPIO.setup(DIR, GPIO.OUT)

def loop():
    print("pulse...")
    while True:
        GPIO.output(DIR, False)  # 设定正方向
        one_step(15000)  # 产生周期为2*82us的脉冲信号
        time.sleep(1000 * ms)  # 延时暂停

        GPIO.output(DIR, True)      # 设定反方向
        one_step(15000)             # 产生周期为2*82us的脉冲信号
        time.sleep(1000 * ms)




def destroy():
    GPIO.output(DIR, False)
    GPIO.output(PUL, False)
    GPIO.cleanup()  # Release resource


if __name__ == '__main__':  # Program start from here
    setup()
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child function destroy() will be  executed.
        print("stop...")
        destroy()



