#!/usr/bin/env python
# -*- coding:utf-8 -*-
#########################################################
#   File name:  y_drive.py
#      Author:  钟东佐
#       Date        ||      describe
#   2020/08/10      ||  Y轴底层驱动，body前后运动控制轴
#   2021/03/01      ||  通过调用 pul_wid_ari.generate() 函数生成脉冲列表
#                   ||  DISPLAY=:0.0
#   2021/04/12      ||  基于新加速算法，调整代码调用，整理了代码
#########################################################
"""
    调用该模块中的 move 实现y轴的运动控制，
    目前规定y轴向前面板方向为正

"""
import RPi.GPIO as GPIO
import wiringpi
import time
import math
import matplotlib.pyplot as plt
import motor.pulse_width_arithmetic as pul_wid_ari

##########################################################################
# 常数值设定区域
Y_PUL = 8           # Y轴脉冲控制信号，8
Y_DIR = 7           # Y轴方向控制信号，False是向前，True是向后，7
# 用于控制运动方向
Y_BACK = True
Y_FRONT = False
UNIT_STEP_MM = 29.96 * 1e-3        # 设定单位步长，由实际测了计算获知，1000细分

VELOCITY_MIN = 0.0005                # 设定最小速度 m/s
VELOCITY_MAX = 0.2                  # 设定最大速度 m/s
RPM_MIN = 1                         # 设定最小转速，启动速度 r/min
RPM_MAX = 400                       # 设定最大转速，最高速度 r/min
ACC_STEP_RPM = 10                   # 设定加减速的rpm阶梯高度
ACC_STEP_TIME = 5000               # 设定加减速中每个阶梯的时间, us

PULSE_REV = 1000                    # 驱动器设定好的细分参数，一圈对应多少脉冲
MM_REV = 29.96                      # 机械结构轨道运动距离与电机旋转的圈数关系，mm / 圈
##########################################################################


def one_step(direction, step_num, rpm_max_specify):
    """
    根据设定调用算法计算出脉冲列表，按照列表执行控制
    用于控制树莓派io口输出电平控制电机驱动器的方向和脉冲

    Parameters
    ----------
    direction
        方向
    step_num
        需要运动的脉冲数，既步数
    rpm_max_specify
        最高转速

    """
    # 设定运动方向
    if direction == 'y_front':
        GPIO.output(Y_DIR, Y_FRONT)   # 设定Y轴向前运动
    elif direction == 'y_back':
        GPIO.output(Y_DIR, Y_BACK)    # 设定Y轴向后运动
    else:
        print('Y轴没有指定方向，请检查')
        return

    # Y轴运动
    # 通过算法得出脉冲列表
    pulse_width_math_list, rpm_math_list = pul_wid_ari.generate(
        step_num=step_num,
        rpm_min=RPM_MIN,                        # 设定最小速度 m/s
        rpm_max=rpm_max_specify,                # 设定最大速度 m/s
        acc_step_rpm=ACC_STEP_RPM,              # 设定加减速的rpm阶梯高度
        acc_step_time=ACC_STEP_TIME,            # 设定加减速中每个阶梯的时间, us

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
    # ax1 = fig.add_subplot(2, 1, 1)
    # ax1.plot(pulse_width_math_list)
    # ax2 = fig.add_subplot(2, 1, 2)
    # ax2.plot(rpm_math_list)
    # plt.show()


def setup():
    """
    初始化设定

    """
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)        # Numbers GPIOs by physical location
    # print('setup y_drive is board')
    GPIO.setup(Y_PUL, GPIO.OUT)     # Set pin's mode is output
    GPIO.setup(Y_DIR, GPIO.OUT)
    GPIO.output(Y_DIR, True)       # 控制前设定方向为默认值向后
    GPIO.output(Y_PUL, False)       # 控制前设定脉冲为默认值高电平

    return True


def move(distance, rpm_max_specify=None):
    """
    y轴依据距离及最高转速的设定，计算出行对应的步数，调用脉冲控制函数实现运动控制

    Parameters
    ----------
    distance
        运动距离，单位为mm。输入值允许正负，且依据正负进行正负向运动
    rpm_max_specify
        最高转速指定，默认为该模块设定的RPM_MAX，指定可在 1-RPM_MAX之间的任意整数值

    """
    # 设定单位步长，由实际测了计算获知
    unit_step = UNIT_STEP_MM
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

    # 设定最高速度，没有指定将按照默认的RPM_MAX
    if rpm_max_specify:
        if 1 <= rpm_max_specify <= RPM_MAX:
            rpm_max = rpm_max_specify
        else:
            print("############################################################################################")
            print("y轴最高转速设定值不在范围[%s, %s]rpm内，不符合要求，强制设定为 %s rpm" % (RPM_MIN, RPM_MAX, RPM_MAX))
            print("############################################################################################")
            rpm_max = RPM_MAX
    else:
        rpm_max = RPM_MAX

    # 调用控制程序控制运动
    print("163：%s加速至最高转度 %s rpm运动 %s 步" % (direction, rpm_max, step_num_value))
    one_step(direction, step_num_value, rpm_max)                            # y轴运动
    return step_num, unit_step


# 循环部分
def main():
    print("pulse...")
    i = 0
    sleep_time = 2
    time.sleep(2)
    while i < 20:
        i = i + 1
        print("Y轴第 %s 次" % i)
        move(8, 4)
        print("暂停")
        time.sleep(sleep_time)
        move(-8)
        print("暂停")
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
