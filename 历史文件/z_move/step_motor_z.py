#!/usr/bin/env python
# -*- coding:utf-8 -*-
#########################################################
#   File name:  step_motor_z.py
#      Author:  钟东佐
#        Date:  2019/07/09
#    describe:  Z轴 28BYJ-48步进电机 底层驱动
#               步进电机分别以单四拍、双四拍、八拍驱动方式驱动，
#               正反转各360度
#########################################################
#########################################################
# 接线方式:
# A ---- 29 ---- OUT1 ---- 橙
# B ---- 31 ---- OUT2 ---- 黄
# C ---- 32 ---- OUT3 ---- 粉（白）
# D ---- 33 ---- OUT4 ---- 蓝
# +   ---- +5V
# -   ---- GND
#########################################################
import RPi.GPIO as GPIO
import time
import wiringpi

# 电机4条控制线连接分配
IN1 = 29
IN2 = 31
IN3 = 32
IN4 = 33
# uchar phasecw[4] ={0x08,0x0c,0x04,0x06,0x02,0x03,0x01,0x09};    # 正转 电机导通相序 D-C-B-A
# uchar phaseccw[4]={0x09,0x01,0x03,0x02,0x06,0x04,0x0c,0x08};    # 反转 电机导通相序 A-B-C-D

# DELAY_NORMAL为正常脉冲间隔，对于控制子函数中直接赋值给delay，调用函数是若需修改可以以实参形式直接复制给delay
DELAY_NORMAL = 3


def set_step(w1, w2, w3, w4):
    GPIO.output(IN1, w1)
    GPIO.output(IN2, w2)
    GPIO.output(IN3, w3)
    GPIO.output(IN4, w4)


def stop():
    set_step(0, 0, 0, 0)
 

def forward(steps, delay=DELAY_NORMAL):
    for i in range(0, steps):
        set_step(1, 0, 0, 0)
        wiringpi.delay(delay)
        set_step(1, 1, 0, 0)
        wiringpi.delay(delay)
        set_step(0, 1, 0, 0)
        wiringpi.delay(delay)
        set_step(0, 1, 1, 0)
        wiringpi.delay(delay)
        set_step(0, 0, 1, 0)
        wiringpi.delay(delay)
        set_step(0, 0, 1, 1)
        wiringpi.delay(delay)
        set_step(0, 0, 0, 1)
        wiringpi.delay(delay)
        set_step(1, 0, 0, 1)
        wiringpi.delay(delay)


def forward_4(steps, delay=DELAY_NORMAL):
    # delay为脉冲间隔，delayMicroseconds是以us为单位，delay是以ms为单位
    for i in range(0, steps):
        set_step(0, 1, 1, 0)
        wiringpi.delay(delay)
        set_step(0, 0, 1, 1)
        wiringpi.delay(delay)
        set_step(1, 0, 0, 1)
        wiringpi.delay(delay)
        set_step(1, 1, 0, 0)
        wiringpi.delay(delay)
 

def backward(steps, delay=DELAY_NORMAL):
    for i in range(0, steps):
        set_step(0, 0, 0, 1)
        wiringpi.delay(delay)
        set_step(0, 0, 1, 1)
        wiringpi.delay(delay)
        set_step(0, 0, 1, 0)
        wiringpi.delay(delay)
        set_step(0, 1, 1, 0)
        wiringpi.delay(delay)
        set_step(0, 1, 0, 0)
        wiringpi.delay(delay)
        set_step(1, 1, 0, 0)
        wiringpi.delay(delay)
        set_step(1, 0, 0, 0)
        wiringpi.delay(delay)
        set_step(1, 0, 0, 1)
        wiringpi.delay(delay)


def backward_4(steps, delay=DELAY_NORMAL):
    # delay为脉冲间隔，delayMicroseconds是以us为单位，delay是以ms为单位
    for i in range(0, steps):
        set_step(1, 1, 0, 0)
        wiringpi.delay(delay)
        set_step(1, 0, 0, 1)
        wiringpi.delay(delay)
        set_step(0, 0, 1, 1)
        wiringpi.delay(delay)
        set_step(0, 1, 1, 0)
        wiringpi.delay(delay)


def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
    GPIO.setup(IN1, GPIO.OUT)      # Set pin's mode is output
    GPIO.setup(IN2, GPIO.OUT)
    GPIO.setup(IN3, GPIO.OUT)
    GPIO.setup(IN4, GPIO.OUT)
 

def loop():
    while True:
        print("stop...")
        stop()
        time.sleep(5)

        print("backward...")
        backward_4(768)  # 512 steps --- 360 angle，0.003

        print("stop...")
        stop()                 # stop
        time.sleep(3)          # sleep 3s

        print("forward...")
        forward_4(768)


def destroy():
    GPIO.cleanup()             # Release resource
 

if __name__ == '__main__':     # Program start from here
    setup()
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child function destroy() will be  executed.
        destroy()
