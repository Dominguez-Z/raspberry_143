#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  z_check.py
#      Author:  钟东佐
#        Date:  2020/12/7
#    describe:  z轴红外检测确定位置
#########################################################
import RPi.GPIO as GPIO
import wiringpi
import time
import motor.z_drive as z
# import math

us = 0.000001   # 微秒的乘数
ms = 0.001      # 毫秒的乘数
Z_PUL = 11      # Z轴脉冲控制信号,11
Z_DIR = 16      # Z轴方向控制信号，False是向右，True是向左,16
Z_CHECK = 20      # z轴光电开关信号接在GPIO20
# 用于控制运动方向
Z_UP = False
Z_DOWN = True
motor_stop = False   # 设定电机停止标志
Z_UNIT_STEP_MM = 50.0625 * 1e-3            # 设定单位步长，由实际测了计算获知，1000细分
# 设定Z轴的运动范围，用于红外检测时的最远距离，Z_RANGE_MM注意正负，正为向上移动，负为向下移动
Z_RANGE_MM = -800
Z_BACK_DISTANCE = 10        # 检测成功后放回的距离，初定10mm
# 单位秒，检测成功后间隔该时间后放回，且2倍值用于下降沿检测间隔设定，避免多次触发回调函数
Z_BACK_SLEEP_TIME = 0.5


# /////////////////////////////////////////////////////////////////////////////////////////
# one_step函数说明
# 该函数用于控制树莓派io口输出电平控制电机驱动器的方向和脉冲
# direction为运动方向，step_num为脉冲数
# pulse_width为脉冲宽度，控制运行速度
##########################################################################
# 常数值设定区域
PULSE_WIDTH_MAX = 3000           # 设定电机启动最大脉冲宽度，值越大速度越小
PULSE_WIDTH_MIN = 800               # 设定电机启动最小脉冲宽度
STEP_NUM_UNIT = Z_UNIT_STEP_MM       # 设定单位步长，由实际测了计算获知
##########################################################################


def one_step(direction, step_num, speed=None):
    # 设定运动方向
    if direction == 'z_up':
        GPIO.output(Z_DIR, Z_UP)  # 设定Z轴向上运动
    elif direction == 'z_down':
        GPIO.output(Z_DIR, Z_DOWN)  # 设定Z轴向下运动
    else:
        print('Z轴没有指定方向，请检查')
        return
    # Z轴运动
    if speed:
        pulse_width_check = PULSE_WIDTH_MIN         # 检测时脉冲宽度设定为Z轴的启动脉冲
    else:
        pulse_width_check = PULSE_WIDTH_MAX         # 检测时脉冲宽度设定为Z轴的启动脉冲
    global motor_stop
    motor_stop = False  # 回程前不管电机停止位是什么，先清零，防止未知电位
    print("57:Motor_Stop = False")
    # 控制电机io电平翻转
    for i in range(0, step_num):
        if not motor_stop:
            # 脉冲产生
            # print(i, pulse_width_math)
            # t1 = wiringpi.micros()
            # t1 = wiringpi.micros()
            GPIO.output(Z_PUL, False)
            # time.sleep(pulse_width_math*us)
            wiringpi.delayMicroseconds(pulse_width_check)
            # t2 = wiringpi.micros()
            GPIO.output(Z_PUL, True)
            # time.sleep(pulse_width_math*us)
            wiringpi.delayMicroseconds(pulse_width_check)
            # print(i, pulse_width_math, t2 - t1)
        elif motor_stop:
            GPIO.output(Z_PUL, True)    # 电机脉冲保持高电平，电机停止运动
            motor_stop = False          # 检测到停止信号后，停止信号清零
            return 'stop_success'
        else:
            print("Z轴停止信号motor_stop不明确")
    return 'stop_not_success'
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


# 边沿检测到后的回调函数
##########################################################################
# 常数值设定区域
# z_check = Z_CHECK
##########################################################################


def my_callback(Z_CHECK):
    global motor_stop
    motor_stop = True               # 将电机停止位置位1,，表示需要停下电机
    print("93:Motor_Stop = True")


# 初始化设定
def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)        # Numbers GPIOs by physical location
    # print('setup z_drive is board')
    GPIO.setup(Z_CHECK, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # 光耦脉冲输入位
    # 对于光耦的信号增加下降边沿检测,开启线程回调
    # bouncetime设定为放回间隔的2倍，防止多次触发回调函数
    GPIO.add_event_detect(Z_CHECK, edge=GPIO.RISING, callback=my_callback,
                          bouncetime=int(Z_BACK_SLEEP_TIME*1000*2))

    return True


# /////////////////////////////////////////////////////////////////////////////////////////
# move函数说明
# z轴距离转步数计算及控制,距离单位为mm
##########################################################################
# 常数值设定区域
UNIT_STEP = Z_UNIT_STEP_MM           # 设定单位步长，由实际测了计算获知
##########################################################################


def move(speed=None):
    distance = Z_RANGE_MM
    if distance >= 0:
        direction = 'z_up'
        distance_back = -Z_BACK_DISTANCE
    elif distance < 0:
        direction = 'z_down'
        distance_back = Z_BACK_DISTANCE
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
        check_state = one_step(direction, step_num_value, speed)    # Z轴运动
    else:
        check_state = one_step(direction, step_num_value)           # Z轴运动
    # check_state: stop_success代表遇到监测点并停下，stop_not_success代表运行到z范围外一直未到监测点
    # 如果检测成功了返回一段距离离开检测物体，避免垂直方向运动撞到
    if check_state == 'stop_success':
        time.sleep(Z_BACK_SLEEP_TIME)
        z.move(distance_back, PULSE_WIDTH_MAX)
    else:
        pass
    return check_state
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


# 循环部分
def loop():
    i = 0
    time.sleep(3)
    print("检测程序开始")
    while i < 5:
        i = i + 1
        z.move(10)
        time.sleep(0.5)
        check_state = move()
        print(check_state)
        time.sleep(5)


# 结束释放
def destroy():
    GPIO.cleanup()              # 释放控制


# 如果该程序为主程序，程序在此开始运行，若不是不运行，该文件只做函数定义
if __name__ == '__main__':  # Program start from here
    z.setup()  # z轴io驱动初始化
    setup_return = setup()
    if setup_return:
        print('z轴检测初始化成功')
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child function destroy() will be  executed.
        print("stop...")
        destroy()
