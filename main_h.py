#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  main_h.py
#      Author:  钟东佐
#       Date        ||      describe
#   2021/04/01      ||  管理主程序main中的setup() 和 destroy()
#########################################################
import RPi.GPIO as GPIO
import sys
import electromagnet.strike_drug_drive as strike_drug
import motor.y_drive as y
import motor.x_drive as x
import motor.z_drive as z
import motor.y1_drive as y1
import motor.x1_drive as x1

# ############################ 常数值设定区域 ############################
ERROR_CHANNEL = 21      # 硬件错误信号输入通道
# ########################################################################


def setup():
    """
    管理主函数的初始化操作，主要包含各模块的初始化setup
    以及本模块的一些GPIO初始化

    Returns
    -------
    return
        正常返回True，任意一个模块初始化错误则返回False
    """
    # #################### 模块初始化 ############################
    z_setup_return = z.setup()
    if not z_setup_return:
        print('Z轴初始化失败')
        return False

    x_setup_return = x.setup()
    if not x_setup_return:
        print('X轴初始化失败')
        return False

    y_setup_return = y.setup()
    if not y_setup_return:
        print('Y轴初始化失败')
        return False

    x1_setup_return = x1.setup()
    if not x1_setup_return:
        print('X1轴初始化失败')
        return False

    y1_setup_return = y1.setup()
    if not y1_setup_return:
        print('Y1轴初始化失败')
        return False

    strike_drug_setup_return = strike_drug.setup()
    if not strike_drug_setup_return:
        print('打药继电器初始化失败')
        return False
    # #################### 本模块初始化 ############################
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)  # Numbers GPIOs by physical location
    # 设置为输入，因为检测上升沿，设置为下拉
    GPIO.setup(ERROR_CHANNEL, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    # 对于硬件出错信号增加上升边沿检测,开启线程回调
    GPIO.add_event_detect(ERROR_CHANNEL, edge=GPIO.RISING, callback=error_stop,bouncetime=100)

    return True


def error_stop(ERROR_CHANNEL):
    """
    检测到硬件错误信号后的回调函数

    """
    print("\n################################")
    print("检测出硬件出错")
    print("################################\n")
    destroy()


def destroy():
    """
        管理主函数的退出时的清除操作，主要包含各模块的释放destroy()

    """
    z.destroy()
    y.destroy()
    x.destroy()
    x1.destroy()
    y1.destroy()
    strike_drug.destroy()
    print("############# 主函数退出 #############")
    sys.exit(0)
