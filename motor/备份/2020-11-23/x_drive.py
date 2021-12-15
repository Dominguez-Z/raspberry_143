#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  x_drive.py
#      Author:  钟东佐
#        Date:  2020/03/25
#    describe:  x轴底层驱动
#########################################################
import RPi.GPIO as GPIO
import wiringpi
import time
import math

us = 0.000001   # 微秒的乘数
ms = 0.001      # 毫秒的乘数
X_PUL = 3  # X轴脉冲控制信号
X_DIR = 5  # X轴方向控制信号，False是向右，True是向左
# 用于控制运动方向
X_LEFT = True
X_RIGHT = False
UNIT_STEP_MM = 90 * 1e-3        # 设定单位步长，由实际测了计算获知

# /////////////////////////////////////////////////////////////////////////////////////////
# one_step函数说明
# 该函数用于控制树莓派io口输出电平控制电机驱动器的方向和脉冲
# direction为运动方向，step_num为脉冲数
# pulse_width为脉冲宽度，控制运行速度
##########################################################################
# 常数值设定区域
PULSE_WIDTH_NORMAL = 120        # 设定X轴的默认脉冲宽度为120us
STEP_NUM_CHANGE_WIDTH = 1 / 10  # 设定加速或减速分别占整个行程的比例，范围0~1
PULSE_WIDTH_MAX = 250           # 设定电机启动最大脉冲宽度，值越大速度越小
STEP_NUM_MIN_MM = 100           # 设定有加减速效果的最小距离，单位是mm，步数小于该值时脉冲宽度设定为最大值
# STEP_NUM_MIN = 1000           # 设定有加减速效果的最小步数，步数小于该值时脉冲宽度设定为最大值
STEP_NUM_UNIT = UNIT_STEP_MM       # 设定单位步长，由实际测了计算获知
##########################################################################


def one_step(direction, step_num, pulse_width=PULSE_WIDTH_NORMAL):
    # 设定运动方向
    if direction == 'x_right':
        GPIO.output(X_DIR, X_RIGHT)   # 设定X轴向右运动
    elif direction == 'x_left':
        GPIO.output(X_DIR, X_LEFT)    # 设定X轴向左运动
    else:
        print('X轴没有指定方向，请检查')
        return
    # X轴运动
    # 1步 = 90um
    # pulse_width最低大概是50
    step_num_change_width = STEP_NUM_CHANGE_WIDTH           # 设定加速或减速分别占整个行程的比例，范围0~1
    pulse_width_max = PULSE_WIDTH_MAX                       # 设定电机启动最大脉冲宽度，值越大速度越小
    step_num_min = round(STEP_NUM_MIN_MM / STEP_NUM_UNIT)   # 计算出有加减速效果的最小步数
    # print(step_num_min)
    if pulse_width > pulse_width_max or pulse_width < 0:
        pulse_width = pulse_width_max
    step_num_speed_up = step_num * step_num_change_width  # 加速停止点
    step_num_speed_down = step_num * (1 - step_num_change_width)  # 减速启动点
    pulse_width_change = pulse_width_max - pulse_width  # 脉冲宽度变化值
    pulse_width_math_list = []  # 创建一个记录脉冲宽度的列表

    ########################################################################################################
    # 脉冲宽度控制算法
    # 用于在x轴远距离运动时，例如拿药，设置脉冲宽度较小，运动速度较快；
    # x轴短距离运动时，例如割药，设置脉冲宽度较大，运动速度较慢，减小启动停止的抖动；
    # 算法核心思想：
    # 设定脉冲的最大值和最小值，创建一个窗函数，使得原本保持最大值的脉冲宽度有一个下降过程达到最小值
    # 在停止前有一个上升过程回到最大值，上升和下降通过三角函数实现。
    ########################################################################################################
    for i in range(0, step_num):
        if step_num < step_num_min:
            pulse_width_math = pulse_width_max
        else:
            if i < step_num_speed_up:
                x = math.pi * i / (step_num * step_num_change_width)
            elif step_num_speed_up <= i < step_num_speed_down:
                x = math.pi
            elif step_num_speed_down <= i <= step_num:
                x = math.pi * (1 + (i - step_num_speed_down) / (step_num * step_num_change_width))
            else:
                x = 0
            amplitude = (math.cos(x) + 1) / 2
            pulse_width_math = round(pulse_width_change * amplitude + pulse_width)
        pulse_width_math_list.append(pulse_width_math)

    # 根据脉冲宽度列表里的值控制电机io电平翻转
    for i in range(0, step_num):
        # 脉冲产生
        # print(i, pulse_width_math_list[i])
        # t1 = wiringpi.micros()
        # t1 = wiringpi.micros()
        GPIO.output(X_PUL, False)
        # time.sleep(pulse_width_math*us)
        wiringpi.delayMicroseconds(pulse_width_math_list[i])
        # t2 = wiringpi.micros()
        GPIO.output(X_PUL, True)
        # time.sleep(pulse_width_math*us)
        wiringpi.delayMicroseconds(pulse_width_math_list[i])
        # print(i, pulse_width_math, t2 - t1)
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


# 初始化设定
def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)        # Numbers GPIOs by physical location
    # print('setup x_drive is board')
    GPIO.setup(X_PUL, GPIO.OUT)     # Set pin's mode is output
    GPIO.setup(X_DIR, GPIO.OUT)
    GPIO.output(X_DIR, True)       # 控制前设定方向为默认值向左
    GPIO.output(X_PUL, True)       # 控制前设定脉冲为默认值高电平

    return True


# /////////////////////////////////////////////////////////////////////////////////////////
# move函数说明
# x轴距离转步数计算及控制,距离单位为mm
##########################################################################
# 常数值设定区域
UNIT_STEP = UNIT_STEP_MM           # 设定单位步长，由实际测了计算获知
##########################################################################


def move(distance):
    # 设定单位步长，由实际测了计算获知
    unit_step = UNIT_STEP
    # 距离取绝对值再计算步数
    step_num_value = round(abs(distance) / unit_step)
    # 根据距离的正负确定运动方向
    if distance >= 0:
        direction = 'x_right'
    elif distance < 0:
        direction = 'x_left'
    else:
        print("函数需要指定方向和大小，正向右，负向左，单位毫米")
        return
    # 输出计算结果以便检测
    # print("139：%s运动距离为：%s" % (direction, step_num_value))
    one_step(direction, step_num_value)  # X轴运动
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


# 循环部分
def loop():
    print("pulse...")
    while True:
        move(200)  # X轴向右运动
        time.sleep(4)  # 延时暂停

        move(-200)  # X轴向左运动
        time.sleep(2)  # 延时暂停


# 结束释放
def destroy():
    GPIO.cleanup()              # 释放控制


# 如果该程序为主程序，程序在此开始运行，若不是不运行，该文件只做函数定义
if __name__ == '__main__':  # Program start from here
    setup_return = setup()
    if setup_return:
        print('x轴初始化成功')
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child function destroy() will be  executed.
        print("stop...")
        destroy()
