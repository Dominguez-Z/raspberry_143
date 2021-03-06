#!/usr/bin/env python 
# -*- coding:utf-8 -*-
import RPi.GPIO as GPIO
import time
import signal
import atexit
import wiringpi

atexit.register(GPIO.cleanup)

servopin = 24
GPIO.setmode(GPIO.BCM)
GPIO.setup(servopin, GPIO.OUT, initial=False)
p = GPIO.PWM(servopin, 50)  # 50HZ
p.start(0)
time.sleep(2)

while True:
    for i in range(0, 181, 45):
        a = (0.5 + i/90)/20 * 100
        p.ChangeDutyCycle(a)  # 设置转动角度
        print(i, a/5)
        time.sleep(0.5)  # 等该20ms周期结束
        p.ChangeDutyCycle(0)  # 设置转动角度
        time.sleep(3)  # 等该20ms周期结束
    for i in range(181, 0, -45):
        a = (0.5 + (i - 1)/90)/20 * 100
        p.ChangeDutyCycle(a)  # 设置转动角度
        print(i, a/5)
        time.sleep(0.5)  # 等该20ms周期结束
        p.ChangeDutyCycle(0)  # 设置转动角度
        time.sleep(3)  # 等该20ms周期结束
    '''
    for i in range(0, 3):
        a = ((i + 1)*0.5 / 20)*100
        p.ChangeDutyCycle(a)  # 设置转动角度
        print(i, a)
        time.sleep(0.75)  # 等该20ms周期结束

    for i in range(0, 3):
        b = ((3 - i) * 0.5 / 20)*100
        p.ChangeDutyCycle(b)
        print(i, b)
        time.sleep(0.75)
    '''

