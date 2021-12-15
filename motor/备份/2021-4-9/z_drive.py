#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  z_drive.py
#      Author:  钟东佐
#       Date        ||      describe
#   2020/03/31      ||  Z轴底层驱动，控制body上下运动
#   2021/03/01      ||  通过调用 pul_wid_ari.generate() 函数生成脉冲列表
#                   ||  DISPLAY=:0.0
#########################################################
import RPi.GPIO as GPIO
import wiringpi
import time
import math
import matplotlib.pyplot as plt
import motor.pulse_width_arithmetic as pul_wid_ari

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
# 原设定Z轴默认脉冲宽度最小为100us，最大为1000
VELOCITY_MIN = 0.00084                # 设定最小速度 m/s
VELOCITY_MAX = 0.5                  # 设定最大速度 m/s
ACC_STEP_RPM = 20                   # 设定加减速的rpm阶梯高度
ACC_STEP = 30                       # 设定加减速的阶梯的宽度
SCALE_PARA = 3                      # 宽度缩放参数，acc_step * (1 - 1/scale_para)

PULSE_REV = 1000                    # 驱动器设定好的细分参数，一圈对应多少脉冲
MM_REV = 50                         # 机械结构轨道运动距离与电机旋转的圈数关系，mm / 圈
##########################################################################


def one_step(direction, step_num, pulse_width=None):
    # 设定运动方向
    if direction == 'z_up':
        GPIO.output(Z_DIR, Z_UP)                    # 设定Z轴向上运动
    elif direction == 'z_down':
        GPIO.output(Z_DIR, Z_DOWN)                  # 设定Z轴向下运动
    else:
        print('Z轴没有指定方向，请检查')
        return
    # Z轴运动
    # 如果脉冲间隔给定，就按照给定值运行
    if pulse_width:
        # 根据脉冲宽度列表里的值控制电机io电平翻转
        for i in range(0, step_num):
            # 脉冲产生
            GPIO.output(Z_PUL, False)
            wiringpi.delayMicroseconds(pulse_width)
            GPIO.output(Z_PUL, True)
            wiringpi.delayMicroseconds(pulse_width)
    # 否则脉冲间隔没有给定，就按照算法实现加减速运行
    else:
        # 通过算法得出脉冲列表
        pulse_width_math_list, rpm_math_list = pul_wid_ari.generate(
            step_num=step_num,
            velocity_min=VELOCITY_MIN,              # 设定最小速度 m/s
            velocity_max=VELOCITY_MAX,              # 设定最大速度 m/s
            acc_step_rpm=ACC_STEP_RPM,              # 设定加减速的rpm阶梯高度
            acc_step=ACC_STEP,                      # 设定加减速的阶梯的宽度
            scale_para=SCALE_PARA,                  # 宽度缩放参数，acc_step * (1 - 1/scale_para)
            
            pulse_rev=PULSE_REV,                    # 驱动器设定好的细分参数，一圈对应多少脉冲
            mm_rev=MM_REV                           # 机械结构轨道运动距离与电机旋转的圈数关系，mm / 圈
        )
         
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
   
        # 输出脉冲图片
        # fig = plt.figure()
        # ax = fig.add_subplot(1, 1, 1)
        # ax.plot(pulse_width_math_list)
        # plt.show()
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


# 初始化设定
def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)              # Numbers GPIOs by physical location
    # print('setup x_drive is board')
    GPIO.setup(Z_PUL, GPIO.OUT)         # Set pin's mode is output
    GPIO.setup(Z_DIR, GPIO.OUT)
    GPIO.output(Z_DIR, False)           # 控制前设定方向为默认值向上
    GPIO.output(Z_PUL, True)            # 控制前设定脉冲为默认值高电平
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
    move(300)
    print("暂停")
    time.sleep(3)

    print("Z轴向下")
    move(-300)
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
        move(300)
        print("暂停")
        time.sleep(3)

        print("Z轴向下第 %s 次" % i)
        move(-300)
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
