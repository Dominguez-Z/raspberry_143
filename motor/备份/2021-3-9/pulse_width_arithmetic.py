#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  pulse_width_arithmetic.py
#      Author:  钟东佐
#       Date        ||      describe
#   2021/03/01      ||  电机脉冲宽度算法,涉及恒定加速度,变阶梯
#                   ||  DISPLAY=:0.0
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
    
    
# /////////////////////////////////////////////////////////////////////////////////////////
# generate函数说明
# 该函数用于接收到相关参数后计算出对应的脉冲宽度列表，
##########################################################################
def generate(
    step_num,                       # 设定脉冲总步数
    velocity_min,                   # 设定最小速度 m/s
    velocity_max,                   # 设定最大速度 m/s
    accelerated,                    # 设定加速度 m/s2，因为加减速对称，只设定一个
    accelerated_step,               # 设定加减速的阶梯数
    acc_para,                       # 加速缩放参数
    dec_para,                       # 减速缩放参数

    pulse_rev,                      # 驱动器设定好的细分参数，一圈对应多少脉冲
    mm_rev                          # 机械结构轨道运动距离与电机旋转的圈数关系，mm / 圈
):
    ###############################################
    # 基础参数计算
    ###############################################
    # 计算出达到最高速的加速时间
    t = (velocity_max - velocity_min) / accelerated			
    # 计算出最小的脉冲宽度，注意速度越大脉冲宽度越小
    pulse_width_min = velo_2_pulwid(velocity_max, pulse_rev, mm_rev)
    # 计算出最大的脉冲宽度
    pulse_width_max = velo_2_pulwid(velocity_min, pulse_rev, mm_rev)			
    # 计算出加速阶梯的脉冲宽度
    acc_step_pul_wid = math.ceil((pulse_width_max - pulse_width_min) / accelerated_step)
    # 输出查看
    print("50：脉冲宽度最短：%s us；最长：%s us,脉冲阶梯变化量：%s" % (pulse_width_min, pulse_width_max, acc_step_pul_wid))
    # 脉冲间隔的加速度 a=(v2-u2)/2s
    accelerated_pul = (pulse_width_max**2 - pulse_width_min**2)/(2 * t * 10**6)
    pulse_width_math_list = []                              # 创建一个记录脉冲宽度的列表
    pulse_width_change_point = []                           # 记录加速阶段跳变点是在第几个脉冲
    
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
    acc_step_count = 1
    for i in range(0, step_num):
        if i <= (step_num - 1)/2:
            # 前一半的计算
            pulse_width_math = pulse_width_max - i * accelerated_pul
            if pulse_width_math >= pulse_width_min:
                if pulse_width_math >= (pulse_width_max - acc_step_count * acc_step_pul_wid):
                    pulse_width_math = pulse_width_max - (acc_step_count-1) * acc_step_pul_wid
                else:
                    pulse_width_math = pulse_width_max - acc_step_count * acc_step_pul_wid
                    acc_step_count += 1
                    pulse_width_change_point.append([i, int(pulse_width_math)])
            else:
                acc_step_count = 1
                pulse_width_math = pulse_width_min
        else:
            # 后一半复制前面的
            pulse_width_math = pulse_width_math_list[(step_num - 1) - i]
        # 更新脉冲宽度列表  
        pulse_width_math_list.append(int(pulse_width_math)) 
    
    ###############################################
    # 对原来的脉冲列表进行变换，使得加速时间减少
    # 如果由于脉冲步数过少未产生阶梯便无需变换
    ###############################################
    print("91：脉冲变化次数：%s" % len(pulse_width_change_point))
    # 判断是否有阶梯产生
    if len(pulse_width_change_point) <= 0:
        pass
    else:
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
    
    return pulse_width_math_list
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


# 初始化设定
def setup():
    
    return True


# 循环部分
def main():
    distance = 0.1              # 单位：mm
    unit_step = 50.0407 * 1e-3  # 设定单位步长，由实际测了计算获知
    step_num = round(abs(distance) / unit_step)
    print(step_num)
    pulse_width_math_list = generate(
        step_num=step_num,
        velocity_min=0.05,       # 设定最小速度 m/s
        velocity_max=0.55,         # 设定最大速度 m/s
        accelerated=0.5,          # 设定加速度 m/s2，因为加减速对称，只设定一个
        accelerated_step=30,      # 设定加减速的阶梯数
        acc_para=0.6,             # 加速缩放参数
        dec_para=0.7,             # 减速缩放参数

        pulse_rev=1000,           # 驱动器设定好的细分参数，一圈对应多少脉冲
        mm_rev=50                 # 机械结构轨道运动距离与电机旋转的圈数关系，mm / 圈
    )
    # 输出脉冲图片
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(pulse_width_math_list)
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
