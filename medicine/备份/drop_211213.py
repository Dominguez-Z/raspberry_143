#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  drop.py
#      Author:  钟东佐
#       Date        ||      describe
#   2021/05/19      ||  编写控制掉药的代码
#########################################################
"""
该模块主要处理药兜中已有药，控制实现掉到药盒里面
执行 do 函数

"""

import time
import os
import json
import motor.y_drive as y
import motor.x_drive as x
import motor.z_drive as z
import motor.y1_drive as y1
import motor.x1_drive as x1
import motor.steering_engine as steering_engine
import motor.go as go
import JSON.coordinate_converter as coordinate_converter
import JSON.ark_barrels_coordinates as ark_barrels_coordinates
import JSON.current_coordinates as current_coordinates
import JSON.params_correction as params_correction
import JSON.constant_coordinates as constant_coordinates
import electromagnet.strike_drug_drive as strike
import threading

# ############################################## 常数值设定区域 ##############################################
# 盒子原点坐标，记录为 [0, 0]组盒子 0号位的坐标。
# 最后一位坐标代表盒子打开，二维码压平后的z高度，与盒子口边缘z高度持平
BOX_ORIGIN_COORDINATES = [726, 184.6, -50]
# 不同组盒子中心之间的距离，[x, y]
BOX_DISTANCE = [114.5, 81]
# 同一组盒子中心距离
NUM_DISTANCE = 24.9

# 空中运动轨迹的 [y, z] 的距离,只有长度，不含正负
# MOTION_CURVE = [20, 36.74]
# MOTION_CURVE = [20, 30]
# MOTION_CURVE = [65, 36.74]              # 加了斜台
MOTION_CURVE = [45, 16.74]              # 加了罩子

# ############################################################################################################


def setup_main():
    """
    作为主函数时的初始化

    """
    steering_engine.Servo("drop")       # 初始化舵机

    z_setup_return = z.setup()
    if not z_setup_return:
        print('Z轴初始化失败')
        return False

    x_setup_return = x.setup()
    if not x_setup_return:
        print('X轴初始化失败')
        return False

    y_setup_return = y.setup()
    if not y_setup_return:
        print('Y轴初始化失败')
        return False

    y1_setup_return = y1.setup()
    if not y1_setup_return:
        print('Y1轴初始化失败')
        return False

    x1_setup_return = x1.setup()
    if not x1_setup_return:
        print('X1轴初始化失败')
        return False

    return True


def do(box_matrix, num):
    """
    实现掉药到指定的盒子里

    Parameters
    ----------
    box_matrix
        哪一组药盒？几行几列，[x, y]。
        x - 0开始，顺着x轴正方向增加
        y - 0开始，顺着y轴正方向增加
    num
        目标是该组药盒的第几个盒子。
        0开始，顺x轴正方向增加。

    """
    # ############################################## 常数值设定区域 ##############################################
    # 盒子原点坐标，记录为 [0, 0]组盒子 0号位的坐标。
    # 最后一位坐标代表盒子打开，二维码压平后的z高度，与盒子口边缘z高度持平
    box_origin_coordinates = BOX_ORIGIN_COORDINATES
    # 不同组盒子中心之间的距离，[x, y]
    box_distance = BOX_DISTANCE
    # 同一组盒子中心距离
    num_distance = NUM_DISTANCE

    # 空中运动轨迹的 [y, z] 的距离,只有长度，不含正负
    motion_curve = MOTION_CURVE

    sleep_time = 0.1  # 动作运动间隔的时间
    # ############################################################################################################
    # 1、获取关注点当前坐标
    drop_channel_xyz = coordinate_converter.body_drop_channel()

    # 2、三轴调整位置，去到指定盒子口掉药点
    # 2.1 x轴
    # 目标：盒子x方向中心
    # [0, 0] 号药盒 0号位x中心 + x方向不同盒组增量 - x方向第几个盒口增量
    target_x = box_origin_coordinates[0] + (box_matrix[0] * box_distance[0]) - (num * num_distance)
    # 2.2 z轴
    # 目标：盒子打开口子边缘z坐标 + 掉落轨迹z方向长度
    target_z = box_origin_coordinates[2] + motion_curve[1]
    # 2.3 根据计算运动xz轴
    go.xz(drop_channel_xyz[0], target_x, drop_channel_xyz[2], target_z)
    time.sleep(sleep_time)

    # 2.4 y轴
    # 重新获取关注点当前y坐标
    drop_channel_xyz = coordinate_converter.body_drop_channel()
    # 目标：盒子y方向中心 - 掉落轨迹y方向长度
    # 盒子y方向中心 = [0, 0] 号药盒 y中心 + y方向不同盒组增量
    target_y = box_origin_coordinates[1] + (box_matrix[1] * box_distance[1]) - motion_curve[0]
    # 根据计算运动y轴
    go.only_y(drop_channel_xyz[1], target_y)
    time.sleep(sleep_time)

    # 3、打开出口掉药
    servo = steering_engine.Servo("drop")
    servo.drop_medicine()
    time.sleep(sleep_time)
    return


# 循环部分
def main():
    for i in range(4):
        do([0, 1], i)
        time.sleep(1)
    return


# 结束释放
def destroy():
    z.destroy()
    y.destroy()
    x.destroy()
    y1.destroy()
    x1.destroy()
    return


# 如果该程序为主程序，程序在此开始运行，若不是不运行，该文件只做函数定义
if __name__ == '__main__':  # Program start from here
    setup_return = setup_main()
    if setup_return:
        print('始化成功')
    try:
        main()
    except KeyboardInterrupt:  # 当按下 'Ctrl+C', 子函数 destroy()将会运行，用于停止退出
        print("程序已停止退出...")
        destroy()
