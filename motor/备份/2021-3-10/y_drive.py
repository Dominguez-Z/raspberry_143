#!/usr/bin/env python
# -*- coding:utf-8 -*-
#########################################################
#   File name:  y_drive.py
#      Author:  钟东佐
#       Date        ||      describe
#   2020/08/10      ||  Y轴底层驱动，body前后运动控制轴
#   2021/03/01      ||  通过调用 pul_wid_ari.generate() 函数生成脉冲列表
#                   ||  DISPLAY=:0.0
#########################################################
import RPi.GPIO as GPIO
import wiringpi
import time
import math
import matplotlib.pyplot as plt
import motor.pulse_width_arithmetic as pul_wid_ari

us = 0.000001       # 微秒的乘数
ms = 0.001          # 毫秒的乘数
Y_PUL = 8           # Y轴脉冲控制信号，8
Y_DIR = 7           # Y轴方向控制信号，False是向前，True是向后，7
# 用于控制运动方向
Y_BACK = True
Y_FRONT = False
UNIT_STEP_MM = 29.96 * 1e-3        # 设定单位步长，由实际测了计算获知，1000细分

# /////////////////////////////////////////////////////////////////////////////////////////
# one_step函数说明
# 该函数用于控制树莓派io口输出电平控制电机驱动器的方向和脉冲
# direction为运动方向，step_num为脉冲数
# pulse_width为脉冲宽度，控制运行速度
##########################################################################
# 常数值设定区域
# 原设定Y轴的默认脉冲宽度最小为50us，最大为500
VELOCITY_MIN = 0.01                # 设定最小速度 m/s
VELOCITY_MAX = 0.2                  # 设定最大速度 m/s
ACC_STEP_RPM = 20                   # 设定加减速的rpm阶梯高度
ACC_STEP = 30                       # 设定加减速的阶梯的宽度
SCALE_PARA = 3                      # 宽度缩放参数，acc_step * (1 - 1/scale_para)

PULSE_REV = 1000                    # 驱动器设定好的细分参数，一圈对应多少脉冲
MM_REV = 29.96                      # 机械结构轨道运动距离与电机旋转的圈数关系，mm / 圈
##########################################################################


def one_step(direction, step_num, pulse_width=None):
    # 设定运动方向
    if direction == 'y_front':
        GPIO.output(Y_DIR, Y_FRONT)   # 设定Y轴向前运动
    elif direction == 'y_back':
        GPIO.output(Y_DIR, Y_BACK)    # 设定Y轴向后运动
    else:
        print('Y轴没有指定方向，请检查')
        return
    # Y轴运动
    # 如果脉冲间隔给定，就按照给定值运行
    if pulse_width:
        # 根据脉冲宽度列表里的值控制电机io电平翻转
        for i in range(0, step_num):
            # 脉冲产生
            GPIO.output(Y_PUL, True)
            wiringpi.delayMicroseconds(pulse_width)
            GPIO.output(Y_PUL, False)
            wiringpi.delayMicroseconds(pulse_width)
    # 否则脉冲间隔没有给定，就按照算法实现加减速运行
    else:
        # 通过算法得出脉冲列表
        pulse_width_math_list = pul_wid_ari.generate(
            step_num=step_num,
            velocity_min=VELOCITY_MIN,              # 设定最小速度 m/s
            velocity_max=VELOCITY_MAX,              # 设定最大速度 m/s
            accelerated=ACCELERATED,                # 设定加速度 m/s2，因为加减速对称，只设定一个
            accelerated_step=ACCELERATED_STEP,      # 设定加减速的阶梯数
            acc_para=ACC_PARA,                      # 加速缩放参数
            dec_para=DEC_PARA,                      # 减速缩放参数

            pulse_rev=PULSE_REV,                    # 驱动器设定好的细分参数，一圈对应多少脉冲
            mm_rev=MM_REV                           # 机械结构轨道运动距离与电机旋转的圈数关系，mm / 圈
        )
        
        # 根据脉冲宽度列表里的值控制电机io电平翻转
        for i in range(0, step_num):
            # 脉冲产生
            # print(i, pulse_width_math_list[i])
            # t1 = wiringpi.micros()
            # t1 = wiringpi.micros()
            GPIO.output(Y_PUL, True)
            # time.sleep(pulse_width_math*us)
            wiringpi.delayMicroseconds(pulse_width_math_list[i])
            # t2 = wiringpi.micros()
            GPIO.output(Y_PUL, False)
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
    GPIO.setmode(GPIO.BCM)        # Numbers GPIOs by physical location
    # print('setup y_drive is board')
    GPIO.setup(Y_PUL, GPIO.OUT)     # Set pin's mode is output
    GPIO.setup(Y_DIR, GPIO.OUT)
    GPIO.output(Y_DIR, True)       # 控制前设定方向为默认值向后
    GPIO.output(Y_PUL, False)       # 控制前设定脉冲为默认值高电平

    return True


# /////////////////////////////////////////////////////////////////////////////////////////
# move函数说明
# y轴距离转步数计算及控制,距离单位为mm
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
        direction = 'y_front'
        step_num = step_num_value
    elif distance < 0:
        direction = 'y_back'
        step_num = -step_num_value
    else:
        print("函数需要指定方向和大小，正向前，负向后，单位毫米")
        return
    # 指定了脉冲间隔将匀速行驶
    if pulse_width:
        # 输出计算结果以便检测
        print("153：%s匀速运动距离为：%s" % (direction, step_num_value))
        one_step(direction, step_num_value, pulse_width)            # Y轴匀速运动
    # 没有指定了脉冲间隔将变速行驶
    else:
        # 输出计算结果以便检测
        print("158：%s变速运动距离为：%s" % (direction, step_num_value))
        one_step(direction, step_num_value)                         # Y轴变速运动
    return step_num, unit_step
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


# /////////////////////////////////////////////////////////////////////////////////////////
# move_step函数说明
# 用于直接指定走的步数，避免回程的时候由于前面计算的四舍五入导致的累计误差
# pulse_width指定了将匀速，没有指定将变速
##########################################################################
def move_step(step_num, pulse_width=None):
    # 根据距离的正负确定运动方向
    if step_num >= 0:
        direction = 'y_front'
    elif step_num < 0:
        direction = 'y_back'
    else:
        print("函数需要指定方向和大小，正向前，负向后，单位毫米")
        return
    # 指定了脉冲间隔将匀速行驶
    if pulse_width:
        # 输出计算结果以便检测
        print("188：%s匀速运动距离为：%s" % (direction, abs(step_num)))
        one_step(direction, abs(step_num), pulse_width)                    # Y轴匀速运动
    # 没有指定了脉冲间隔将变速行驶
    else:
        # 输出计算结果以便检测
        print("186：%s变速运动距离为：%s" % (direction, abs(step_num)))
        one_step(direction, abs(step_num))                                 # Y轴变速运动
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


# 循环部分
def main():
    print("pulse...")
    i = 0
    sleep_time = 1
    time.sleep(2)
    while i < 20:
        i = i + 1
        print("Y轴第 %s 次" % i)
        move(70)
        time.sleep(sleep_time)
        move(-70)
        time.sleep(sleep_time)

        # print("Y轴第 %s 次" % i)
        # # Y轴前进到达对准位判断位置是否正确
        # move(-1, 1000)
        # time.sleep(sleep_time)
        # # Y轴运动将铁片插入最下药板和上一片药板之间，然后Z轴提高至药板槽与药板卡位相平的位置
        # move(13.5, 1000)
        # time.sleep(sleep_time)
        # # Y轴进一步插入，使得药片板位于夹片之间准备夹取
        # move(4.7, 1000)
        # time.sleep(sleep_time)
        # # Y轴和Y1轴慢速反向运动，把拉钩拉入药板槽，加紧药板
        # move(5.5, 3360)
        # time.sleep(sleep_time)
        # # Y轴完全拉出，恢复到起始位置
        # back_l = -(79.6 + 13.5 + 4.7)
        # move(back_l)
        # time.sleep(sleep_time)
        # # Y轴前进到达对准位判断位置是否正确
        # move(75.6)
        # time.sleep(sleep_time)
        # # Y轴运动将铁片插入最下药板之下，然后Z轴提高至药板槽与药板卡位相平的位置
        # move(6.5, 1000)
        # time.sleep(sleep_time)
        # # Y轴进一步插入
        # move(15.7, 1000)
        # time.sleep(sleep_time)
        # # Y轴和Y1轴慢速反向运动，放松药板
        # move(-5.5, 3360)
        # time.sleep(sleep_time)
        # # Y轴完全拉出，恢复到起始位置
        # back_l = -(79.6 + 13.5 + 4.7)
        # move(back_l)
        # time.sleep(sleep_time)


# 结束释放
def destroy():
    GPIO.cleanup()              # 释放控制


# 如果该程序为主程序，程序在此开始运行，若不是不运行，该文件只做函数定义
if __name__ == '__main__':  # Program start from here
    setup_return = setup()
    if setup_return:
        print('y轴初始化成功')
    try:
        main()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child function destroy() will be  executed.
        print("stop...")
        destroy()
