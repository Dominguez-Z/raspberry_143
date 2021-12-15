#!/usr/bin/env python 
# -*- coding:utf-8 -*-

import math
import wiringpi

step_num = 20000
pulse_width = 100


step_num_change_width = 1 / 10  # 设定加速或减速分别占整个行程的比例，范围0~1
pulse_width_max = 1000  # 设定电机启动最大脉冲宽度，值越大速度越小
step_num_min = 100  # 设定有加减速效果的最小步数，步数小于该值时脉冲宽度设定为最大值
if pulse_width > pulse_width_max or pulse_width < 0:
    pulse_width = pulse_width_max
step_num_speed_up = step_num * step_num_change_width  # 加速停止点
step_num_speed_down = step_num * (1 - step_num_change_width)  # 减速启动点
pulse_width_change = pulse_width_max - pulse_width  # 脉冲宽度变化值
pulse_width_math_list = []      # 创建一个记录脉冲宽度的列表


########################################################################################################
# 脉冲宽度控制算法
# 用于在x轴远距离运动时，例如拿药，设置脉冲宽度较小，运动速度较快；
# x轴短距离运动时，例如割药，设置脉冲宽度较打，运动速度较慢，减小启动停止的抖动；
# 算法核心思想：
# 设定脉冲的最大值和最小值，创建一个窗函数，使得原本保持最大值的脉冲宽度有一个下降过程达到最小值
# 在停止前有一个上升过程回到最大值，上升和下降通过三角函数实现。
########################################################################################################
for i in range(0, step_num):
    # 用于计算脉冲宽度计算时间
    t1 = wiringpi.micros()
    t1 = wiringpi.micros()
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
    t2 = wiringpi.micros()

t = t2 - t1
print("计算存储完成，用时%s" % t)

for i in range(0, step_num):
    print(i, pulse_width_math_list[i])

print(len(pulse_width_math_list))
print("输出完成，计算用时%s" % t)
