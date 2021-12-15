#!/usr/bin/env python
#########################################################
#   File name: 57_step_Motor.py
#      Author: ZDZ
#        Date: 2018/12/25
#########################################################
import RPi.GPIO as GPIO
import time

PUL = 11  # pin11
DIR = 13
uS = 0.000001   # 微秒的乘数
mS = 0.001      # 毫秒的乘数

# def setStep(w1, w2, w3, w4):
#     GPIO.output(IN1, w1)
#     GPIO.output(IN2, w2)
#     GPIO.output(IN3, w3)
#     GPIO.output(IN4, w4)
#
# def stop():
#     setStep(0, 0, 0, 0)

def pulse_82us(duration):         # width的大小最小为0.000001，但是宽度为60到80us不等。
    for i in range(0, int(duration / (0.000082*2) ) ):      # duration为脉冲持续时间
        time.sleep(0.0004)
        GPIO.output(PUL, False)
        time.sleep(0.0004)
        GPIO.output(PUL, True)

def backward(delay, steps):
    for i in range(0, steps):
        setStep(0, 0, 0, 1)
        time.sleep(delay)
        setStep(0, 0, 1, 1)
        time.sleep(delay)
        setStep(0, 0, 1, 0)
        time.sleep(delay)
        setStep(0, 1, 1, 0)
        time.sleep(delay)
        setStep(0, 1, 0, 0)
        time.sleep(delay)
        setStep(1, 1, 0, 0)
        time.sleep(delay)
        setStep(1, 0, 0, 0)
        time.sleep(delay)
        setStep(1, 0, 0, 1)
        time.sleep(delay)

def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)    # Numbers GPIOs by physical location
    GPIO.setup(PUL, GPIO.OUT)   # Set pin's mode is output
    GPIO.setup(DIR, GPIO.OUT)

def loop():
    # p = GPIO.PWM(PUL, 100000)
    print("pulse...")
    while True:
        GPIO.output(DIR, False)     # 设定正方向
        pulse_82us(0.5)             # 产生周期为2*82us的脉冲信号
        pulse_82us(0.0005)
        time.sleep(50*mS)           # 延时暂停

        GPIO.output(DIR, True)      # 设定反方向
        pulse_82us(0.5)             # 产生周期为2*82us的脉冲信号
        time.sleep(50 * mS)


def destroy():
    #p.stop()
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



