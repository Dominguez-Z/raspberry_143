#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  pulse_width_arithmetic.py
#      Author:  钟东佐
#       Date        ||      describe
#   2021/03/01      ||  电机脉冲宽度算法,涉及恒定加速度,变阶梯
#                   ||  DISPLAY=:0.0
#   2021/03/09      ||  加速算法由脉冲宽度转化为rpm再转回脉冲宽度
#   2021/03/10      ||  加速算法改为先构成rpm列表，再转化为脉冲宽度
#   2021/04.09      ||  修改加速算法，输入为rpm范围，计算基于每个阶梯的持续时间
#########################################################
import RPi.GPIO as GPIO
import wiringpi
import time
import matplotlib.pyplot as plt
import math


def velo_2_pulwid(velocity, pulse_rev, mm_rev):
    # 速度转脉冲宽度
    pulse_width_us = 1000 * mm_rev / (pulse_rev * velocity)
    return int(pulse_width_us)


def velo_2_rpm(velocity, mm_rev):
    # 速度转rpm，转每分钟
    rpm = 60 * 1000 * velocity / mm_rev
    return int(rpm)


def rpm_2_velo(rpm, mm_rev):
    """
    rpm转速度，m/s

    Parameters
    ----------
    rpm
        转速，转每分钟
    mm_rev
        机械结构轨道运动距离与电机旋转的圈数关系，mm / 圈

    Returns
    -------
    round(rpm, 7)
        速度，m/s,最小去到0.1um

    """
    velocity = rpm * mm_rev / (60 * 1000)
    return round(velocity, 7)


def rpm_2_pulwid(rpm, pulse_rev):
    # rpm转脉冲宽度，us
    pulse_width_us = 1000 * 60 * 1000 / (rpm * pulse_rev)
    return int(pulse_width_us)


def pulwid_2_rpm(pulwid, pulse_rev):
    # 脉冲宽度转rpm，转每分钟
    rpm = 1000 * 60 * 1000 / (pulwid * pulse_rev)
    return int(rpm)

    
# /////////////////////////////////////////////////////////////////////////////////////////
# generate函数说明
# 该函数用于接收到相关参数后计算出对应的脉冲宽度列表，
##########################################################################
def generate(
    step_num,
    rpm_min,
    rpm_max,
    acc_step_rpm,
    acc_step_time,

    pulse_rev,
    mm_rev
):
    """
    接收到相关参数后计算出对应的脉冲宽度列表。

    Parameters
    ----------
    step_num
        设定脉冲总步数
    rpm_min
        设定最小转速，启动速度 r/min
    rpm_max
        设定最大转速，最高速度 r/min
    acc_step_rpm
        设定加减速的rpm阶梯高度
    acc_step_time
        设定加减速中每个阶梯的时间, us
    pulse_rev
        驱动器设定好的细分参数，一圈对应多少脉冲
    mm_rev
        机械结构轨道运动距离与电机旋转的圈数关系，mm / 圈

    Returns
    -------
    Return
        脉冲宽度列表
    """

    # ##############################################
    # 基础参数计算
    # ##############################################
    # 计算出最小、最大的速度，输出观察
    velocity_min = rpm_2_velo(rpm_min, mm_rev)
    velocity_max = rpm_2_velo(rpm_max, mm_rev)
    print("86:电机启动速度为：%s m/s,最高速度为：%s m/s" % (velocity_min, velocity_max))
    print("加数时间：%s ms" % (math.ceil((rpm_max - rpm_min)/acc_step_rpm) * acc_step_time / 1000))

    rpm_step_state = []                 # 记录变速阶段每个rpm占了多少个脉冲，不包含最高速度
    # 计算加速总阶梯数
    rpm_step_now = rpm_min
    while rpm_step_now < rpm_max:
        # 计算当前转速对应的 脉冲宽度
        pulwid = rpm_2_pulwid(rpm_step_now, pulse_rev)
        # 向上取整计算每个阶梯对于该脉冲宽度允许有几个脉冲
        pulwid_num = math.ceil(acc_step_time / pulwid)
        # print("脉冲宽度：%s，脉冲持续次数：%s" % (pulwid, pulwid_num))
        # 添加 [转速，持续脉冲数]
        rpm_step_state.append([rpm_step_now, pulwid_num])
        rpm_step_now += acc_step_rpm
    # print("rpm持续列表为：\n %s" % rpm_step_state)

    # 记录变速阶段跳变中，每一个rpm最后的脉冲数[change_point, rpm]
    rpm_change_point = []
    change_point = 0
    for i in range(len(rpm_step_state)):
        change_point += rpm_step_state[i][1]
        rpm_change_point. append([change_point, rpm_step_state[i][0]])
    # print("变速阶段跳变转换点：\n %s" % rpm_change_point)
    # print("135：脉冲变化次数：%s" % len(rpm_change_point))
    # rpm转化us
    pulse_width_change_point = [[i[0], rpm_2_pulwid(i[1], pulse_rev)] for i in rpm_change_point]
    # print("脉冲宽度变速阶段跳变转换点：\n %s" % pulse_width_change_point)

    rpm_math_list = []                  # 创建一个记录转速的列表

    ########################################################################################################
    # 脉冲宽度控制算法
    # 算法核心思想：
    #
    ########################################################################################################
    acc_step_num = len(rpm_step_state)
    acc_step_count = 0

    for i in range(0, step_num):
        if i <= (step_num - 1)/2:
            # 前一半的计算
            if acc_step_count < (acc_step_num - 1):
                if i < rpm_change_point[acc_step_count][0]:
                    rpm_math = rpm_change_point[acc_step_count][1]
                else:
                    rpm_math = rpm_change_point[acc_step_count+1][1]
                    acc_step_count += 1
            elif acc_step_count == (acc_step_num - 1):
                if i < rpm_change_point[acc_step_count][0]:
                    rpm_math = rpm_change_point[acc_step_count][1]
                else:
                    rpm_math = rpm_max
                    acc_step_count += 1
            else:
                rpm_math = rpm_max
        else:
            # 后一半复制前面的
            rpm_math = rpm_math_list[(step_num - 1) - i]
        # 更新脉冲宽度列表  
        rpm_math_list.append(int(rpm_math))

    ###############################################
    # 对原来的脉冲列表进行变换，元素变为rpm，使得rpm的变为匀速增加
    # 如果由于脉冲步数过少未产生阶梯便无需变换
    ###############################################

    # 输出查看
    if step_num != 0:
        print("104：实际转速最慢：%s rpm；最快：%s rpm" % (rpm_math_list[0], rpm_math_list[int((step_num - 1) / 2)]))
    else:
        print("116：实际转速最慢：0 rpm；最快：0 rpm")
    # rpm转化us
    pulse_width_return_list = [rpm_2_pulwid(i, pulse_rev) for i in rpm_math_list]
    # 输出查看
    if step_num != 0:
        print("121：脉冲宽度最短：%s us；最长：%s us"
              % (pulse_width_return_list[int((step_num - 1) / 2)], pulse_width_return_list[0]))
    else:
        print("121：脉冲宽度最短：无限 us；最长：无限 us")
    
    return pulse_width_return_list, rpm_math_list
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


# 初始化设定
def setup():
    
    return True


# 循环部分
def main():
    distance = 300              # 单位：mm
    unit_step = 50.0407 * 1e-3  # 设定单位步长，由实际测了计算获知
    step_num = round(abs(distance) / unit_step)
    print("186:%s" % step_num)
    pulse_width_math_list, rpm_math_list = generate(
        step_num=step_num,
        rpm_min=1,
        rpm_max=600,
        acc_step_rpm=10,
        acc_step_time=8000,

        pulse_rev=1000,           # 驱动器设定好的细分参数，一圈对应多少脉冲
        mm_rev=50                 # 机械结构轨道运动距离与电机旋转的圈数关系，mm / 圈
    )
    # 输出脉冲图片
    fig = plt.figure()
    ax1 = fig.add_subplot(2, 1, 1)
    ax1.plot(pulse_width_math_list)
    ax2 = fig.add_subplot(2, 1, 2)
    ax2.plot(rpm_math_list)
    plt.show()
    return


# 结束释放
def destroy():
    return


# 如果该程序为主程序，程序在此开始运行，若不是不运行，该文件只做函数定义
if __name__ == '__main__':  # Program start from here
    setup_return = setup()
    if setup_return:
        print('步进电机脉冲宽度算法驱动成功')
    try:
        main()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child function destroy() will be  executed.
        print("stop...")
        destroy()
