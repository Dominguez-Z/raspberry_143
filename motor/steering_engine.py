#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  steering_engine.py
#      Author:  钟东佐
#       Date        ||      describe
#   2021/05/19      ||  舵机驱动
#########################################################
"""
调用函数 drive 驱动舵机
"""
import RPi.GPIO as GPIO
import time
import signal
import atexit
import wiringpi
##########################################################################
# 常数值设定区域
SERVO_PIN = 24
CLOSE_ANGLE = 165
OPEN_ANGLE = 120

##########################################################################


def setup():
    """
    初始化设定

    """
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SERVO_PIN, GPIO.OUT, initial=False)
    turn_to(CLOSE_ANGLE)

    return True


def turn_to(angle):
    """
    转动到指定角度停下

    Parameters
    ----------
    angle
        目标角度，范围值 0 - 180

    """
    p = GPIO.PWM(SERVO_PIN, 50)  # 50HZ
    # 启动pwm
    p.start(0)

    time.sleep(0.5)

    a = (0.5 + angle / 90) / 20 * 100
    p.ChangeDutyCycle(a)        # 设置转动角度
    time.sleep(0.5)             # 等该转动到位结束
    p.stop()
    # p.ChangeDutyCycle(0)        # 输出置零，停止脉冲输出
    # time.sleep(0.5)


def main():
    """
    主函数

    """
    while True:

        turn_to(OPEN_ANGLE)
        time.sleep(1)
        turn_to(CLOSE_ANGLE)
        time.sleep(1)


# 结束释放
def destroy():
    GPIO.cleanup()              # 释放控制


# 如果该程序为主程序，程序在此开始运行，若不是不运行，该文件只做函数定义
if __name__ == '__main__':  # Program start from here
    setup_return = setup()
    if setup_return:
        print('舵机初始化成功')
    try:
        main()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child function destroy() will be  executed.
        print("stop...")
        destroy()
