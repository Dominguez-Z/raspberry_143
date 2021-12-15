#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# 加速减速算法2
# 匀加速控制

import math
import wiringpi
# import matplotlib
# matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

distance = 200                      # 单位：mm
unit_step = 50.0407 * 1e-3        # 设定单位步长，由实际测了计算获知
step_num = round(abs(distance) / unit_step)


velocity_min = 0.025     # 设定最小速度 m/s
velocity_max = 0.5      # 设定最大速度 m/s
accelerated = 0.5       # 设定加速度 m/s2，因为加减速对称，只设定一个
accelerated_step = 11   # 设定加减速的阶梯数

pulse_rev = 1000        # 驱动器设定好的细分参数，一圈对应多少脉冲
mm_rev = 50             # 机械结构轨道运动距离与电机旋转的圈数关系，mm / 圈

def velo_2_pulwid(velocity):
    # 速度转脉冲宽度
    pulse_width_us = 1000 * mm_rev / (pulse_rev * velocity)
    return int(pulse_width_us)

t = (velocity_max - velocity_min) / accelerated			# 计算出达到最高速的加速时间
pulse_width_min = velo_2_pulwid(velocity_max)			# 计算出最小的脉冲宽度，注意速度越大脉冲宽度越小
pulse_width_max = velo_2_pulwid(velocity_min)			# 计算出最大的脉冲宽度
# 计算出加速阶梯的脉冲宽度
acc_step_pul_wid = (pulse_width_max - pulse_width_min) / accelerated_step
# 脉冲间隔的加速度
accelerated_pul = (pulse_width_max**2 - pulse_width_min**2)/(2 * t * 10**(6))

print(accelerated_pul)

pulse_width_change = pulse_width_max - pulse_width_min  # 脉冲宽度变化值
pulse_width_math_list = []              # 创建一个记录脉冲宽度的列表
pulse_width_change_point = []           # 记录加速阶段跳变点是在第几个脉冲

# 用于计算脉冲宽度计算时间
t1 = wiringpi.micros()
t1 = wiringpi.micros()
########################################################################################################
# 脉冲宽度控制算法
# 用于在x轴远距离运动时，例如拿药，设置脉冲宽度较小，运动速度较快；
# x轴短距离运动时，例如割药，设置脉冲宽度较打，运动速度较慢，减小启动停止的抖动；
# 算法核心思想：
########################################################################################################
acc_step_count = 1
for i in range(0, step_num):
    if i <= (step_num - 1)/2:
        # 前一半的计算
        pulse_width_math = pulse_width_max - i * accelerated_pul
        if pulse_width_math >= pulse_width_min:
            if pulse_width_math >= (pulse_width_max - acc_step_count * acc_step_pul_wid):
                pulse_width_math = pulse_width_max - (acc_step_count-1) * acc_step_pul_wid
            else:
                pulse_width_math = pulse_width_max - acc_step_count  * acc_step_pul_wid

                pulse_width_change_point.append([i, int(pulse_width_math)])
                acc_step_count += 1
        else:
            acc_step_count = 1
            pulse_width_math = pulse_width_min
    else:
        # 后一半复制前面的
        pulse_width_math = pulse_width_math_list[(step_num - 1) - i]
    pulse_width_math_list.append(int(pulse_width_math))

t2 = wiringpi.micros()

t = t2 - t1
print("计算存储完成，用时%s" % t)

for i in range(0, step_num):
    print(i, pulse_width_math_list[i])

print(len(pulse_width_math_list))
print("输出完成，计算用时%s" % t)

###############################################
# 对原来的脉冲列表进行变换，使得加速时间减少
###############################################
print(pulse_width_change_point)
pulse_width_change_point_acc = []           # 记录新加速阶段跳变点是在第几个脉冲
pulse_width_change_point_dec = []           # 记录新减速阶段跳变点是在第几个脉冲
# 对加速跳变点的横坐标进行缩放,pwcp * acc_para * 1/(1+j)
pwcp_end = 2*pulse_width_change_point[len(pulse_width_change_point)-1][0] - pulse_width_change_point[len(pulse_width_change_point)-2][0]
acc_para = 0.7
j = 0
for i in range(len(pulse_width_change_point)-1, -1, -1):
    pwcp = pulse_width_change_point[i][0]
    pulse_width_change_point_acc.insert(0, [int(pwcp * acc_para * 1/(1+j)), pulse_width_change_point[i][1]])
    j += 1
# 脉冲跳变表最前面添加[0, pulse_width_max],最后面添加[（原有最后跳变点）, pulse_width_min]
pulse_width_change_point_acc.insert(0, [0, pulse_width_max])
pulse_width_change_point_acc.append([pwcp_end, pulse_width_min])
print(pulse_width_change_point_acc)

# 对减速跳变点的横坐标进行缩放
dec_para = 0.7
k = 0
"""
for i in range(len(pulse_width_change_point)-1, -1, -1):
    pwcp = pulse_width_change_point[i][0]
    pulse_width_change_point_dec.insert(0, [int(step_num - pwcp * acc_para * 1/(1+k)), pulse_width_change_point[i][1]])
    k += 1
# 脉冲跳变表最前面添加[（step_num -原有加速最后跳变点）, pulse_width_min],最后面添加[step_num, pulse_width_max]
pulse_width_change_point_dec.append([(step_num - pwcp_end), pulse_width_min])
pulse_width_change_point_dec.insert(0, [step_num, pulse_width_max])
"""
for i in range(0, len(pulse_width_change_point)):
    pwcp = pwcp_end - pulse_width_change_point[i][0]
    pwcp_scale = int(pwcp * dec_para * 1 / (1 + k))
    pulse_width_change_point_dec.append([step_num - (pwcp_end - pwcp_scale), pulse_width_change_point[i][1]])
    k += 1
# 脉冲跳变表最前面添加[（step_num -原有加速最后跳变点）, pulse_width_min],最后面添加[step_num, pulse_width_max]
pulse_width_change_point_dec.append([(step_num - pwcp_end), pulse_width_min])
pulse_width_change_point_dec.insert(0, [step_num, pulse_width_max])
print(pulse_width_change_point_dec)

# 根据新的脉冲跳变表修改原来的脉冲表
acc_step_num = len(pulse_width_change_point_acc)
acc_step_count = 1
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
        
fig  = plt.figure()
ax = fig.add_subplot(1,1,1)
ax.plot(pulse_width_math_list)
plt.show()


