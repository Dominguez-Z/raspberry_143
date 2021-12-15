#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  y_check.py
#      Author:  钟东佐
#        Date:  2020/04/30
#    describe:  y轴红外检测确定位置
#########################################################
import RPi.GPIO as GPIO
import wiringpi
import time
import motor.y_drive as y
# import math

us = 0.000001       # 微秒的乘数
ms = 0.001          # 毫秒的乘数
Y_PUL = 8           # Y轴脉冲控制信号
Y_DIR = 7           # Y轴方向控制信号，False是向下，True是向上
Y_CHECK = 20        # Y轴光电开关信号接在GPIO20
# 用于控制运动方向
Y_BACK = True
Y_FRONT = False
motor_stop = False   # 设定电机停止标志
Y_UNIT_STEP_MM = 29.96 * 1e-3            # 设定单位步长，由实际测了计算获知，1000细分
# 设定Y轴的运动范围，用于红外检测时的最远距离，Y_RANGE_MM注意正负，正为向右移动，负为向左移动
Y_RANGE_MM = -200
Y_BACK_DISTANCE = 10        # 检测成功后放回的距离
# 单位秒，检测成功后间隔改时间后放回，且2倍值用于下降沿检测间隔设定，避免多次触发回调函数
Y_BACK_SLEEP_TIME = 0.5


# /////////////////////////////////////////////////////////////////////////////////////////
# one_step函数说明
# 该函数用于控制树莓派io口输出电平控制电机驱动器的方向和脉冲
# direction为运动方向，step_num为脉冲数
# pulse_width为脉冲宽度，控制运行速度
##########################################################################
# 常数值设定区域
PULSE_WIDTH_MAX = 2000           # 设定电机启动最大脉冲宽度，值越大速度越小
PULSE_WIDTH_MIN = 500           # 设定电机启动最小脉冲宽度
STEP_NUM_UNIT = Y_UNIT_STEP_MM       # 设定单位步长，由实际测了计算获知
##########################################################################


def one_step(direction, step_num, speed=None):
    # 设定运动方向
    if direction == 'y_front':
        GPIO.output(Y_DIR, Y_FRONT)  # 设定Y轴向前运动
    elif direction == 'y_back':
        GPIO.output(Y_DIR, Y_BACK)  # 设定Y轴向后运动
    else:
        print('Y轴没有指定方向，请检查')
        return
    # Y轴运动
    # 1步 = 90.14um
    if speed:
        pulse_width_check = PULSE_WIDTH_MIN  # 检测时脉冲宽度设定为Y轴的启动脉冲
    else:
        pulse_width_check = PULSE_WIDTH_MAX     # 检测时脉冲宽度设定为Y轴的启动脉冲
    global motor_stop
    motor_stop = False  # 回程前不管电机停止位是什么，先清零，防止未知电位
    print("Motor_Stop = False")
    # 控制电机io电平翻转
    for i in range(0, step_num):
        if not motor_stop:
            # 脉冲产生
            # print(i, pulse_width_math)
            # t1 = wiringpi.micros()
            # t1 = wiringpi.micros()
            GPIO.output(Y_PUL, False)
            # time.sleep(pulse_width_math*us)
            wiringpi.delayMicroseconds(pulse_width_check)
            # t2 = wiringpi.micros()
            GPIO.output(Y_PUL, True)
            # time.sleep(pulse_width_math*us)
            wiringpi.delayMicroseconds(pulse_width_check)
            # print(i, pulse_width_math, t2 - t1)
        elif motor_stop:
            GPIO.output(Y_PUL, True)    # 电机脉冲保持高电平，电机停止运动
            motor_stop = False          # 检测到停止信号后，停止信号清零
            return 'stop_success'
        else:
            print("Y轴停止信号motor_stop不明确")
    return 'stop_not_success'
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


# 边沿检测到后的回调函数
##########################################################################
# 常数值设定区域
# y_check = Y_CHECK
##########################################################################


def my_callback(Y_CHECK):
    global motor_stop
    motor_stop = True               # 将电机停止位置位1,，表示需要停下电机
    print("94:Motor_Stop = True")


# 初始化设定
def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)        # Numbers GPIOs by physical location
    # print('setup y_drive is board')
    GPIO.setup(Y_CHECK, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # 光耦脉冲输入位
    # 对于光耦的信号增加上升边沿检测,开启线程回调
    # bouncetime设定为放回间隔的2倍，防止多次触发回调函数
    GPIO.add_event_detect(Y_CHECK, edge=GPIO.RISING, callback=my_callback,
                          bouncetime=int(Y_BACK_SLEEP_TIME*1000*2))

    return True


# /////////////////////////////////////////////////////////////////////////////////////////
# move函数说明
# Y轴距离转步数计算及控制,距离单位为mm
##########################################################################
# 常数值设定区域
UNIT_STEP = Y_UNIT_STEP_MM           # 设定单位步长，由实际测了计算获知
##########################################################################


def move(speed=None):
    distance = Y_RANGE_MM
    if distance >= 0:
        direction = 'y_front'
        distance_back = -Y_BACK_DISTANCE
    elif distance < 0:
        direction = 'y_back'
        distance_back = Y_BACK_DISTANCE
    else:
        print("函数需要指定方向和大小，正向右，负向左，单位毫米")
        return
    # 设定单位步长，由实际测了计算获知
    unit_step = UNIT_STEP
    # 距离取绝对值再计算步数
    step_num_value = round(abs(distance) / unit_step)
    # 输出计算结果以便检测
    # print("运动距离为：%s" % step_num_value)
    if speed:
        check_state = one_step(direction, step_num_value, speed)  # Y轴运动
    else:
        check_state = one_step(direction, step_num_value)  # Y轴运动
    # check_state: stop_success代表遇到监测点并停下，stop_not_success代表运行到Y范围外一直未到监测点
    # 如果检测成功了返回一段距离离开检测物体，避免垂直方向运动撞到
    if check_state == 'stop_success':
        time.sleep(Y_BACK_SLEEP_TIME)
        y.move(distance_back, PULSE_WIDTH_MAX)
    else:
        pass
    return check_state
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


# 循环部分
def loop():
    i = 0
    time.sleep(3)
    print("检测程序开始")
    while i < 50:
        i = i + 1
        print(i)
        y.move(10)
        time.sleep(0.5)
        check_state = move()
        print(check_state)
        time.sleep(2)


# 结束释放
def destroy():
    GPIO.cleanup()              # 释放控制


# 如果该程序为主程序，程序在此开始运行，若不是不运行，该文件只做函数定义
if __name__ == '__main__':  # Program start from here
    y.setup()  # Y轴io驱动初始化
    setup_return = setup()
    if setup_return:
        print('Y轴检测初始化成功')
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child function destroy() will be  executed.
        print("stop...")
        destroy()

