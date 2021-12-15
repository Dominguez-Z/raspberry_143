#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  z_drive.py
#      Author:  钟东佐
#        Date:  2020/03/31
#    describe:  z轴底层驱动
#########################################################
import RPi.GPIO as GPIO
import wiringpi
import time
import math

us = 0.000001   # 微秒的乘数
ms = 0.001      # 毫秒的乘数
Z_PUL = 11       # Z轴脉冲控制信号,11
Z_DIR = 16      # Z轴方向控制信号,16
# 用于控制运动方向
Z_UP = False
Z_DOWN = True
UNIT_STEP_MM = 50.0625 * 1e-3        # 设定单位步长，由实际测了计算获知，1000细分


# /////////////////////////////////////////////////////////////////////////////////////////
# one_step函数说明
# 该函数用于控制树莓派io口输出电平控制电机驱动器的方向和脉冲
# direction为运动方向，step_num为脉冲数
# pulse_width为脉冲宽度，控制运行速度
##########################################################################
# 常数值设定区域
PULSE_WIDTH_NORMAL_UP = 100         # 设定Z轴向上的默认脉冲宽度为100us
PULSE_WIDTH_NORMAL_DOWN = 100       # 设定Z轴向下的默认脉冲宽度为100us
STEP_NUM_CHANGE_WIDTH = 1 / 10      # 设定加速或减速分别占整个行程的比例，范围0~1
PULSE_WIDTH_MAX = 1000               # 设定电机启动最大脉冲宽度，值越大速度越小
# 正常750，转药瓶3000
STEP_NUM_MIN_MM = 100               # 设定有加减速效果的最小距离，单位是mm，步数小于该值时脉冲宽度设定为最大值
# STEP_NUM_MIN = 1000               # 设定有加减速效果的最小步数，步数小于该值时脉冲宽度设定为最大值
STEP_NUM_UNIT = UNIT_STEP_MM        # 设定单位步长，由实际测了计算获知
##########################################################################


def one_step(direction, step_num, pulse_width=None):
    # Z轴运动
    # 1步 = 90um
    # pulse_width最低大概是250
    # 如果脉冲间隔给定，就按照给定值运行
    if pulse_width:
        # 设定运动方向
        if direction == 'z_up':
            GPIO.output(Z_DIR, Z_UP)                    # 设定Z轴向上运动
        elif direction == 'z_down':
            GPIO.output(Z_DIR, Z_DOWN)                  # 设定Z轴向下运动
        else:
            print('Z轴没有指定方向，请检查')
            return
        # 根据脉冲宽度列表里的值控制电机io电平翻转
        for i in range(0, step_num):
            # 脉冲产生
            GPIO.output(Z_PUL, False)
            wiringpi.delayMicroseconds(pulse_width)
            GPIO.output(Z_PUL, True)
            wiringpi.delayMicroseconds(pulse_width)
    # 否则脉冲间隔没有给定，就按照算法实现加减速运行
    else:
        # 设定运动方向和pulse_width在向上和向下的不同值
        if direction == 'z_up':
            GPIO.output(Z_DIR, Z_UP)                    # 设定Z轴向上运动
            pulse_width = PULSE_WIDTH_NORMAL_UP
        elif direction == 'z_down':
            GPIO.output(Z_DIR, Z_DOWN)                  # 设定Z轴向下运动
            pulse_width = PULSE_WIDTH_NORMAL_DOWN
        else:
            print('Z轴没有指定方向，请检查')
            return
        step_num_change_width = STEP_NUM_CHANGE_WIDTH               # 设定加速或减速分别占整个行程的比例，范围0~1
        pulse_width_max = PULSE_WIDTH_MAX                           # 设定电机启动最大脉冲宽度，值越大速度越小
        step_num_min = round(STEP_NUM_MIN_MM / STEP_NUM_UNIT)       # 计算出有加减速效果的最小步数
        # print("54：计算出有加减速效果的最小步数为%s" % step_num_min)
        # 判断pulse_width值是否超出最大值范围，超出了强制变成最大值，避免计算出现负值
        if pulse_width > pulse_width_max or pulse_width < 0:
            pulse_width = pulse_width_max
        step_num_speed_up = step_num * step_num_change_width            # 加速停止点
        step_num_speed_down = step_num * (1 - step_num_change_width)    # 减速启动点
        pulse_width_change = pulse_width_max - pulse_width              # 脉冲宽度变化值
        pulse_width_math_list = []                                      # 创建一个记录脉冲宽度的列表

        ########################################################################################################
        # 脉冲宽度控制算法
        # 用于在Z轴远距离运动时，例如拿药，设置脉冲宽度较小，运动速度较快；
        # Z轴短距离运动时，例如压药，设置脉冲宽度较大，运动速度较慢，减小启动停止的抖动；
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
            GPIO.output(Z_PUL, False)
            # time.sleep(pulse_width_math*us)
            wiringpi.delayMicroseconds(pulse_width_math_list[i])
            # t2 = wiringpi.micros()
            GPIO.output(Z_PUL, True)
            # time.sleep(pulse_width_math*us)
            wiringpi.delayMicroseconds(pulse_width_math_list[i])
            # print(i, pulse_width_math, t2 - t1)
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


# 初始化设定
def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)        # Numbers GPIOs by physical location
    # print('setup x_drive is board')
    GPIO.setup(Z_PUL, GPIO.OUT)     # Set pin's mode is output
    GPIO.setup(Z_DIR, GPIO.OUT)
    GPIO.output(Z_DIR, False)       # 控制前设定方向为默认值向上
    GPIO.output(Z_PUL, True)       # 控制前设定脉冲为默认值高电平
    return True


# /////////////////////////////////////////////////////////////////////////////////////////
# move函数说明
# z轴距离转步数计算及控制,距离单位为mm
# pulse_width指定了将匀速，没有指定将变速
##########################################################################
# 常数值设定区域
UNIT_STEP = UNIT_STEP_MM           # 设定单位步长，由实际测了计算获知
##########################################################################


def move(distance, pulse_width=None):
    # 设定单位步长，由实际测了计算获知
    unit_step = UNIT_STEP
    # 距离取绝对值再计算步数
    step_num_value = round(abs(distance) / unit_step)
    # 根据距离的正负确定运动方向
    if distance >= 0:
        direction = 'z_up'
        step_num = step_num_value
    elif distance < 0:
        direction = 'z_down'
        step_num = -step_num_value
    else:
        print("函数需要指定方向和大小，正向右，负向左，单位毫米")
        return
    # 指定了脉冲间隔将匀速行驶
    if pulse_width:
        # 输出计算结果以便检测
        print("167：%s匀速运动距离为：%s" % (direction, step_num_value))
        one_step(direction, step_num_value, pulse_width)                    # Z轴匀速运动
    # 没有指定了脉冲间隔将变速行驶
    else:
        # 输出计算结果以便检测
        print("172：%s变速运动距离为：%s" % (direction, step_num_value))
        one_step(direction, step_num_value)                                 # Z轴变速运动
    return step_num, unit_step                                        # 返回走的步数和步距
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


# /////////////////////////////////////////////////////////////////////////////////////////
# move_step函数说明
# 用于直接指定走的步数，避免回程的时候由于前面计算的四舍五入导致的累计误差
# pulse_width指定了将匀速，没有指定将变速
##########################################################################
def move_step(step_num, pulse_width=None):
    # 根据距离的正负确定运动方向
    if step_num >= 0:
        direction = 'z_up'
    elif step_num < 0:
        direction = 'z_down'
    else:
        print("函数需要指定方向和大小，正向右，负向左，单位毫米")
        return
    # 指定了脉冲间隔将匀速行驶
    if pulse_width:
        # 输出计算结果以便检测
        print("166：%s匀速运动距离为：%s" % (direction, abs(step_num)))
        one_step(direction, abs(step_num), pulse_width)                    # Z轴匀速运动
    # 没有指定了脉冲间隔将变速行驶
    else:
        # 输出计算结果以便检测
        print("171：%s变速运动距离为：%s" % (direction, abs(step_num)))
        one_step(direction, abs(step_num))                                 # Z轴变速运动
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


# z轴控制测试，距离单位为mm, z_up, z_down
def move_test():

    print("Z轴向上")
    move(400)
    print("暂停")
    time.sleep(3)

    print("Z轴向下")
    move(-400)
    print("暂停")
    time.sleep(3)


# 循环部分
def main():
    print("pulse...")
    i = 0
    time.sleep(3)
    while i < 50:
        i = i + 1
        print("Z轴向上第 %s 次" % i)
        move(500)
        print("暂停")
        time.sleep(3)

        print("Z轴向下第 %s 次" % i)
        move(-500)
        print("暂停")
        time.sleep(3)


# 结束释放
def destroy():
    GPIO.cleanup()              # 释放控制


# 如果该程序为主程序，程序在此开始运行，若不是则不运行，该文件只做函数定义
if __name__ == '__main__':  # Program start from here
    setup_return = setup()
    if setup_return:
        print('Z轴初始化成功')
    try:
        main()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child function destroy() will be  executed.
        print("stop...")
        destroy()
