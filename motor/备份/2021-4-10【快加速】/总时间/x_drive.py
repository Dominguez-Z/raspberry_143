#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  x_drive.py
#      Author:  钟东佐
#       Date        ||      describe
#   2020/03/25      ||  X轴底层驱动，控制body左右运动
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
X_PUL = 19      # X轴脉冲控制信号,19
X_DIR = 26      # X轴方向控制信号，False是向右，True是向左,26
# 用于控制运动方向
X_LEFT = True
X_RIGHT = False
UNIT_STEP_MM = 50.0407 * 1e-3        # 设定单位步长，由实际测了计算获知，1000细分

# /////////////////////////////////////////////////////////////////////////////////////////
# one_step函数说明
# 该函数用于控制树莓派io口输出电平控制电机驱动器的方向和脉冲
# direction为运动方向，step_num为脉冲数
# pulse_width为脉冲宽度，控制运行速度
##########################################################################
# 常数值设定区域
RPM_MIN = 1                         # 设定最小转速，启动速度 r/min
RPM_MAX = 200                       # 设定最大转速，最高速度 r/min
ACC_STEP_RPM = 10                   # 设定加减速的rpm阶梯高度
ACC_TIME = 500                      # 设定加减速时间, ms

PULSE_REV = 1000                    # 驱动器设定好的细分参数，一圈对应多少脉冲
MM_REV = 50                         # 机械结构轨道运动距离与电机旋转的圈数关系，mm / 圈
##########################################################################


def one_step(direction, step_num, pulse_width=None):
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
    # 如果脉冲间隔给定，就按照给定值运行
    if pulse_width:
        # 根据脉冲宽度列表里的值控制电机io电平翻转
        for i in range(0, step_num):
            # 脉冲产生
            GPIO.output(X_PUL, False)
            wiringpi.delayMicroseconds(pulse_width)
            GPIO.output(X_PUL, True)
            wiringpi.delayMicroseconds(pulse_width)
    # 否则脉冲间隔没有给定，就按照算法实现加减速运行
    else:
        # 通过算法得出脉冲列表
        pulse_width_math_list, rpm_math_list = pul_wid_ari.generate(
            step_num=step_num,
            rpm_min=RPM_MIN,                        # 设定最小速度 m/s
            rpm_max=RPM_MAX,                        # 设定最大速度 m/s
            acc_step_rpm=ACC_STEP_RPM,              # 设定加减速的rpm阶梯高度
            acc_time=ACC_TIME,                      # 设定加减速时间, ms
            
            pulse_rev=PULSE_REV,                    # 驱动器设定好的细分参数，一圈对应多少脉冲
            mm_rev=MM_REV                           # 机械结构轨道运动距离与电机旋转的圈数关系，mm / 圈
        )
                
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

        # 输出脉冲图片
        # fig = plt.figure()
        # ax1 = fig.add_subplot(2, 1, 1)
        # ax1.plot(pulse_width_math_list)
        # ax2 = fig.add_subplot(2, 1, 2)
        # ax2.plot(rpm_math_list)
        # plt.show()
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


# 初始化设定
def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)        # Numbers GPIOs by physical location
    # print('setup x_drive is board')
    GPIO.setup(X_PUL, GPIO.OUT)     # Set pin's mode is output
    GPIO.setup(X_DIR, GPIO.OUT)
    GPIO.output(X_DIR, True)       # 控制前设定方向为默认值向左
    GPIO.output(X_PUL, True)       # 控制前设定脉冲为默认值高电平

    return True


# /////////////////////////////////////////////////////////////////////////////////////////
# move函数说明
# x轴距离转步数计算及控制,距离单位为mm
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
        direction = 'x_left'
        step_num = step_num_value
    elif distance < 0:
        direction = 'x_right'
        step_num = -step_num_value
    else:
        print("函数需要指定方向和大小，正向右，负向左，单位毫米")
        return
    # 指定了脉冲间隔将匀速行驶
    if pulse_width:
        # 输出计算结果以便检测
        print("153：%s匀速运动距离为：%s" % (direction, step_num_value))
        one_step(direction, step_num_value, pulse_width)            # X轴匀速运动
    # 没有指定了脉冲间隔将变速行驶
    else:
        # 输出计算结果以便检测
        print("158：%s变速运动距离为：%s" % (direction, step_num_value))
        one_step(direction, step_num_value)                         # X轴变速运动
    return step_num, unit_step

# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


# /////////////////////////////////////////////////////////////////////////////////////////
# position_fine_tuning 函数说明
# 位置微调时调用该函数
# 微调距离在0-2mm之内,步进单位约是50um，5丝
##########################################################################
def position_fine_tuning(distance):
    if 0 < abs(distance) <= 2:
        step_num_value, unit_step = move(distance, 4000)    # 微小的移动使用较大的脉冲宽度是的机械振动减小
        return step_num_value, unit_step
    else:
        print("输入距离并非0-2mm之间，不适合使用位置微调函数")
        return
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


# /////////////////////////////////////////////////////////////////////////////////////////
# move_step函数说明
# 用于直接指定走的步数，避免回程的时候由于前面计算的四舍五入导致的累计误差
# pulse_width指定了将匀速，没有指定将变速
##########################################################################
def move_step(step_num, pulse_width=None):
    # 根据距离的正负确定运动方向
    if step_num >= 0:
        direction = 'x_right'
    elif step_num < 0:
        direction = 'x_left'
    else:
        print("函数需要指定方向和大小，正向右，负向左，单位毫米")
        return
    # 指定了脉冲间隔将匀速行驶
    if pulse_width:
        # 输出计算结果以便检测
        print("188：%s匀速运动距离为：%s" % (direction, abs(step_num)))
        one_step(direction, abs(step_num), pulse_width)                    # X轴匀速运动
    # 没有指定了脉冲间隔将变速行驶
    else:
        # 输出计算结果以便检测
        print("186：%s变速运动距离为：%s" % (direction, abs(step_num)))
        one_step(direction, abs(step_num))                                 # X轴变速运动
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


# 循环部分
def main():
    print("pulse...")
    i = 0
    time.sleep(3)
    while i < 50:
        i = i + 1

        print("X轴向左第 %s 次" % i)
        # position_fine_tuning(0.5)
        move(1)
        print("暂停")
        time.sleep(2)

        print("X轴向右 %s 次" % i)
        # position_fine_tuning(-0.5)
        move(-1)
        print("暂停")
        time.sleep(2)
        '''
        # print("X轴向左第 %s 次" % i)
        # # position_fine_tuning(0.5)
        # move(-0.2, 4000)
        # print("暂停")
        # time.sleep(2)

        print("X轴向左第 %s 次" % i)
        # position_fine_tuning(0.5)
        move(-0.6, 4000)
        print("暂停")
        time.sleep(2)

        print("X轴向右 %s 次" % i)
        # position_fine_tuning(-0.5)
        move(0.8, 4000)
        print("暂停")
        time.sleep(2)

        # print("X轴向左第 %s 次" % i)
        # # position_fine_tuning(0.5)
        # move(-0.4, 4000)
        # print("暂停")
        # time.sleep(2)

        print("X轴向左第 %s 次" % i)
        # position_fine_tuning(0.5)
        move(-1, 4000)
        print("暂停")
        time.sleep(2)

        print("X轴向右 %s 次" % i)
        # position_fine_tuning(-0.5)
        move(1.2, 4000)
        print("暂停")
        time.sleep(2)

        print("X轴向左第 %s 次" % i)
        # position_fine_tuning(0.5)
        move(-0.6, 4000)
        print("暂停")
        time.sleep(2)
        '''
        # time.sleep(2)


# 结束释放
def destroy():
    GPIO.cleanup()              # 释放控制


# 如果该程序为主程序，程序在此开始运行，若不是不运行，该文件只做函数定义
if __name__ == '__main__':  # Program start from here
    setup_return = setup()
    if setup_return:
        print('x轴初始化成功')
    try:
        main()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child function destroy() will be  executed.
        print("stop...")
        destroy()
