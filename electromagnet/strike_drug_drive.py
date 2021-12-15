#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  strike_drug_drive.py
#      Author:  钟东佐
#        Date:  2020/12/08
#    describe:  打药点击驱动程序，控制继电器的开闭
#########################################################

import RPi.GPIO as GPIO
import time
import motor.go as go
import motor.y_drive as y
import motor.x_drive as x
import motor.z_drive as z
import motor.y1_drive as y1
import GPIO.define as gpio_define

STRIKE_SIGNAL = gpio_define.BM_HIT          # 继电器控制信号
STRIKE_TIME_NORMAL = 0.3    # 设定默认打药时间，单位是秒
# 硬件低电平有效
ENABLED = False
DISABLE = True

def setup():
    """
    模块初始化设定

    """
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)        # Numbers GPIOs by physical location
    # print('setup x1_drive is board')
    GPIO.setup(STRIKE_SIGNAL, GPIO.OUT)     # Set pin's mode is output
    GPIO.output(STRIKE_SIGNAL, DISABLE)       # 输出未使能，意为不击打

    return True


def setup_main():
    """
    作为主函数时的初始化

    """
    # 补充本模块的初始化
    setup()

    z_setup_return = z.setup()
    if not z_setup_return:
        print('Z轴初始化失败')

    x_setup_return = x.setup()
    if not x_setup_return:
        print('X轴初始化失败')

    y_setup_return = y.setup()
    if not y_setup_return:
        print('Y轴初始化失败')

    y1_setup_return = y1.setup()
    if not y1_setup_return:
        print('Y1轴初始化失败')
    return True


# /////////////////////////////////////////////////////////////////////////////////////////
# 函数说明，执行了按照指定的时间打药，未指定时间则按照默认的时间打药
##########################################################################
def do(t=None):
    # 如果指定了打药时间，按照指定进行
    if t:
        # 输出计算结果以便检测
        print("39：打药时间为指定的：%s秒" % t)
        # 打药
        time.sleep(0.1)
        GPIO.output(STRIKE_SIGNAL, ENABLED)
        time.sleep(t)
        GPIO.output(STRIKE_SIGNAL, DISABLE)
        time.sleep(0.1)
        return
    # 没有指定时间，便按照默认时间进行
    else:
        t_normal = STRIKE_TIME_NORMAL  # 将时间设定为默认打药时间
        # 输出计算结果以便检测
        print("44：打药时间为默认的：%s秒" % t_normal)
        # 打药
        time.sleep(0.1)
        GPIO.output(STRIKE_SIGNAL, ENABLED)
        time.sleep(t_normal)
        GPIO.output(STRIKE_SIGNAL, DISABLE)
        time.sleep(0.1)
        return
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


# 循环部分
def main():
    # go.only_x(0, -0.5, 2000)
    # time.sleep(2)
    # go.only_y(0, -0.5, 1000)
    # time.sleep(2)
    print("开始测试打药")
    i = 0
    time.sleep(2)
    while i < 3:
        # go.only_y1(26 + 14.385 * i, 1000)
        # time.sleep(2)
        print(i)
        i = i + 1
        do(0.3)
        time.sleep(2)


def destroy():
    """
    退出时的释放

    """
    GPIO.cleanup()              # 释放控制


# 如果该程序为主程序，程序在此开始运行，若不是不运行，该文件只做函数定义
if __name__ == '__main__':  # Program start from here
    setup_return = setup_main()
    if setup_return:
        print('打药初始化成功')
    try:
        main()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child function destroy() will be  executed.
        print("stop...")
        destroy()
