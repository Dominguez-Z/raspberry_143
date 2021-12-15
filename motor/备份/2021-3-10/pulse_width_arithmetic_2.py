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


def rpm_2_pulwid(rpm, pulse_rev):
    # rpm转脉冲宽度
    pulse_width_us = 1000 * 60 * 1000 / (rpm * pulse_rev)
    return int(pulse_width_us)


def pulwid_2_rpm(pulwid, pulse_rev):
    # rpm转脉冲宽度
    rpm = 1000 * 60 * 1000 / (pulwid * pulse_rev)
    return int(rpm)

    
# /////////////////////////////////////////////////////////////////////////////////////////
# generate函数说明
# 该函数用于接收到相关参数后计算出对应的脉冲宽度列表，
##########################################################################
def generate(
    step_num,                       # 设定脉冲总步数
    velocity_min,                   # 设定最小速度 m/s
    velocity_max,                   # 设定最大速度 m/s
    acc_step_rpm,                   # 设定加减速的rpm阶梯高度
    acc_step,                       # 设定加减速的阶梯的宽度

    pulse_rev,                      # 驱动器设定好的细分参数，一圈对应多少脉冲
    mm_rev                          # 机械结构轨道运动距离与电机旋转的圈数关系，mm / 圈
):
    ###############################################
    # 基础参数计算
    ###############################################		
    # 计算出最小的转速
    rpm_min = velo_2_rpm(velocity_min, mm_rev)
    # 计算出最大的转速
    rpm_max = velo_2_rpm(velocity_max, mm_rev)
    # 输出查看
    # print("64：脉冲宽度最短：%s us；最长：%s us" % (pulse_width_min, pulse_width_max))
    print("65：设定转速最慢：%s rpm；最快：%s rpm" % (rpm_min, rpm_max))
    # 脉冲间隔的加速度 a=(v2-u2)/2s
    rpm_math_list = []                  # 创建一个记录转速的列表
    rpm_change_point = []               # 记录加速阶段跳变点是在第几个脉冲
    ########################################################################################################
    # 脉冲宽度控制算法
    # 算法核心思想：
    # 1、构造匀加速的脉冲列表，变速过程是直线
    # 2、对变速过程进行阶梯变化，使得某一个脉冲宽度可以持续一段脉冲次数，使得磁场的建立可以在每个阶段持续一段时间，加速稳定些。
    # 3、根据不同的脉冲宽度修改对应的脉冲次数，实现脉冲宽度大(速度慢)时，阶梯脉冲数较小。使得速度快的占比较大，加速时间减少。
    ########################################################################################################
    ###############################################
    # 形成匀加速的阶梯
    ###############################################
    acc_step_count = 0
    for i in range(0, step_num):
        if i <= (step_num - 1)/2:
            # 前一半的计算
            rpm_math = rpm_min + acc_step_count * acc_step_rpm
            if rpm_math <= rpm_max:
                # if i <= math.ceil((acc_step_count + 1) * acc_step * (1 - 0.5 ** (acc_step_count + 1))) - 1:
                if i <= (acc_step_count + 1) * acc_step - 1:
                    pass
                else:
                    acc_step_count += 1
                    rpm_change_point.append([i, int(rpm_math)])
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
    print("102：实际脉冲变化次数：%s" % len(rpm_change_point))
    # 输出查看
    print("104：实际转速最慢：%s rpm；最快：%s rpm" % (rpm_math_list[0], rpm_math_list[int((step_num - 1) / 2)]))
    # rpm转化us
    pulse_width_return_list = [rpm_2_pulwid(i, pulse_rev) for i in rpm_math_list]
    # 输出查看
    print("108：脉冲宽度最短：%s us；最长：%s us" \
          % (pulse_width_return_list[int((step_num - 1) / 2)], pulse_width_return_list[0]))
    """
    # 判断是否有阶梯产生
    if len(pulse_width_change_point) <= 0:
        pulse_width_return_list = pulse_width_math_list
    else:
        # us转化rpm
        rpm_math_list = [pulwid_2_rpm(i, pulse_rev) for i in pulse_width_math_list]
        rpm_min = rpm_math_list[0]
        rpm_max = rpm_math_list[int((step_num - 1)/2)]
        print(len(pulse_width_change_point), rpm_min, rpm_max)
        print(pulse_width_change_point)
        acc_step_rpm = math.ceil((rpm_max - rpm_min) / len(pulse_width_change_point))
        ###############################################
        # 根据新的脉冲跳变表修改原来的脉冲表
        ###############################################
        acc_step_num = len(pulse_width_change_point)
        acc_step_count = 0
        for i in range(0, step_num):
            if i <= (step_num - 1)/2:
                # 前一半的计算
                if acc_step_count < acc_step_num:
                    if i <= pulse_width_change_point[acc_step_count][0]:
                        rpm_math_list[i] = rpm_min + acc_step_count * acc_step_rpm
                    else:
                        acc_step_count += 1
                        rpm_math_list[i] = rpm_min + acc_step_count * acc_step_rpm
                else:
                    rpm_math_list[i] = rpm_min + acc_step_count * acc_step_rpm
            else:
                # 后一半复制前面的
                rpm_math_list[i] = rpm_math_list[(step_num - 1) - i]
        # rpm转化us
        pulse_width_return_list = [rpm_2_pulwid(i, pulse_rev) for i in rpm_math_list]
        # 输出查看
        print("50：脉冲宽度最短：%s us；最长：%s us,脉冲阶梯变化量：%s" \
              % (pulse_width_return_list[int((step_num - 1) / 2)], pulse_width_return_list[0], acc_step_rpm))
        
        pulse_width_change_point_acc = []           # 记录新加速阶段跳变点是在第几个脉冲
        pulse_width_change_point_dec = []           # 记录新减速阶段跳变点是在第几个脉冲

        # 对跳变点的横坐标进行缩放
        pwcp_end = 2*pulse_width_change_point[len(pulse_width_change_point)-1][0] - \
                   pulse_width_change_point[len(pulse_width_change_point)-2][0]
        # 加速阶段缩放
        j = 0
        for i in range(len(pulse_width_change_point)-1, -1, -1):
            pwcp = pulse_width_change_point[i][0]
            pulse_width_change_point_acc.insert(0, [int(pwcp * acc_para * 1/(1+j)), pulse_width_change_point[i][1]])
            j += 1
        # 脉冲跳变表最前面添加[0, pulse_width_max],最后面添加[（原有最后跳变点）, pulse_width_min]
        pulse_width_change_point_acc.insert(0, [0, pulse_width_max])
        pulse_width_change_point_acc.append([pwcp_end, pulse_width_min])

        # 减速阶段缩放
        k = 0
        for i in range(len(pulse_width_change_point)-1, -1, -1):
            pwcp = pulse_width_change_point[i][0]
            pulse_width_change_point_dec.insert(0, [int(step_num - pwcp * dec_para * 1/(1+k)), pulse_width_change_point[i][1]])
            k += 1
        # 脉冲跳变表最前面添加[（step_num -原有加速最后跳变点）, pulse_width_min],最后面添加[step_num, pulse_width_max]
        pulse_width_change_point_dec.append([(step_num - pwcp_end), pulse_width_min])
        pulse_width_change_point_dec.insert(0, [step_num, pulse_width_max])

        ###############################################
        # 根据新的脉冲跳变表修改原来的脉冲表
        ###############################################
        acc_step_num = len(pulse_width_change_point_acc)
        acc_step_count = 1
        # 加速阶段修改
        for i in range(0, step_num):
            if i <= (step_num - 1)/2:
                if acc_step_count < acc_step_num:
                    if i <= pulse_width_change_point_acc[acc_step_count][0]:
                        pulse_width_math_list[i] = pulse_width_change_point_acc[acc_step_count-1][1]
                    else:
                        pulse_width_math_list[i] = pulse_width_change_point_acc[acc_step_count-1][1]
                        acc_step_count += 1
                else:
                    pass
            else:
                pass
        # 减速阶段修改
        dec_step_num = len(pulse_width_change_point_dec)
        dec_step_count = 1
        for i in range(step_num-1, -1, -1):
            if i >= (step_num - 1)/2:
                if dec_step_count < dec_step_num:
                    if i >= pulse_width_change_point_dec[dec_step_count][0]:
                        pulse_width_math_list[i] = pulse_width_change_point_dec[dec_step_count-1][1]
                    else:
                        pulse_width_math_list[i] = pulse_width_change_point_dec[dec_step_count-1][1]
                        dec_step_count += 1
                else:
                    pass
            else:
                pass
    """
    
    return pulse_width_return_list, rpm_math_list
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


# 初始化设定
def setup():
    
    return True


# 循环部分
def main():
    distance = 20              # 单位：mm
    unit_step = 50.0407 * 1e-3  # 设定单位步长，由实际测了计算获知
    step_num = round(abs(distance) / unit_step)
    print("186:%s" % step_num)
    pulse_width_math_list, rpm_math_list  = generate(
        step_num=step_num,
        velocity_min=0.0016,        # 设定最小速度 m/s
        velocity_max=0.5,           # 设定最大速度 m/s
        acc_step_rpm=10,               # 设定加减速的rpm阶梯高度
        acc_step=30,                   # 设定加减速的阶梯的宽度

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
