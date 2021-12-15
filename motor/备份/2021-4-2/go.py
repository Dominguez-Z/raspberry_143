#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  go.py
#      Author:  钟东佐
#        Date:  2020/4/23
#    describe:  XYZ控制的底层代码封装，调用运动结束会更新坐标到JSON/constant_coordinates.json中
#########################################################
import time
import os
import json
import motor.y_drive as y
import motor.x_drive as x
import motor.z_drive as z
import motor.y1_drive as y1
import motor.x1_drive as x1
from JSON import current_coordinates
import JSON.constant_coordinates as constant_coordinates
import threading

# ############################ 常数值设定区域 ############################
current_path = os.path.dirname(__file__)            # 获取本文件的路径
constant_coordinates_file_path = current_path + "/../JSON/constant_coordinates.json"   # 加上目标文件的相对路径
# 用于指定坐标[x,y,z]中，切片时指定哪一位
# X = 0
# Y = 1
# Z = 2
# 各轴的范围
X_RANGE = [63.1, 1120.1]
Y_RANGE = [64.8, 199]
Z_RANGE = [15.3, 863.3]
X1_RANGE = [28, 69]
Y1_RANGE = [-122, 0]

# 记录坐标的小数位数
RECORD_DECIMALS = 8
# ########################################################################
# CUT_WAIT_COORDINATE_XY =[0, 0]  # xy待切割点坐标


# ############################### 函数说明 ###############################
# xy函数接收以列表的方式接收当前坐标[x0, y0]和目标坐标[x1, y1]
# 创建线程分别控制x、y轴运动
# ########################################################################
def xy(coordinate_now, coordinate_target):
    # 注释掉的判断在上一层做，底层限制太死不方便控制拓展
    """
    # 为保证目前坐标或目标坐标其一是待切割点才运行
    # 避免运动平面撞上其他东西
    cut_wait_coordinate = CUT_WAIT_COORDINATE_XY
    if coordinate_now == cut_wait_coordinate or coordinate_target == cut_wait_coordinate:

    else:
        print("当前坐标或者目标坐标非指定点%s，运动过程可能撞击其他部件，已停止并放回" % cut_wait_coordinate)
        return 'go_xy_error'
    """
    # 通过现有坐标和目的坐标计算需要走的距离，包含正负
    x_distance = coordinate_target[0] - coordinate_now[0]
    y_distance = coordinate_target[1] - coordinate_now[1]
    # 创建x、y轴子线程
    threads = []
    t1 = threading.Thread(target=x.move, args=(x_distance,))
    threads.append(t1)
    t2 = threading.Thread(target=y.move, args=(y_distance,))
    threads.append(t2)
    # 将所有子线程开始
    for t in threads:
        t.setDaemon(True)
        t.start()
    # 打开子线程的阻塞保证所有子线程都运行完了，主线程才继续
    for t in threads:
        t.join()
        # print("threads : %s.time is: %s" % (t, ctime()))
    print('go_xy_success')
    return 'go_xy_success'


# ############################### 函数说明 ###############################
# xy函数接收以列表的方式接收当前坐标[x0, y0]和目标坐标[x1, y1]
# 创建线程分别控制x、y轴运动
# ########################################################################
def xz(coordinate_now_x, coordinate_target_x,
       coordinate_now_z, coordinate_target_z,
       pulse_width_x=None ,pulse_width_z=None):
    """
    创建线程分别控制x、z轴运动，实现时间上同时启动
    
    Parameters
    ----------
    coordinate_now_x
        当前x坐标
    coordinate_target_x
        目标x坐标
    coordinate_now_z
        当前z坐标
    coordinate_target_z
        目标z坐标
    pulse_width_x
        x轴运动脉冲宽度，默认为None，即为变速
    pulse_width_z
        z轴运动脉冲宽度，默认为None，即为变速
    """
    # 创建x、z轴子线程
    threads = []
    t1 = threading.Thread(target=only_x, args=(coordinate_now_x, coordinate_target_x, pulse_width_x,))
    threads.append(t1)
    t2 = threading.Thread(target=only_z, args=(coordinate_now_z, coordinate_target_z, pulse_width_z,))
    threads.append(t2)
    # 将所有子线程开始
    for t in threads:
        t.setDaemon(True)
        t.start()
    # 打开子线程的阻塞保证所有子线程都运行完了，主线程才继续
    for t in threads:
        t.join()
        # print("threads : %s.time is: %s" % (t, ctime()))
    print('go_xz_success')
    return


# ############################### 函数说明 ###############################
# only_y函数接目标坐标,并更新坐标位置
# 控制y轴运动
# ########################################################################
def only_y(coordinate_now, coordinate_target, pulse_width=None):
    current_coordinates_y = current_coordinates.get('motor_y')  # 获取目前主体的坐标
    # 通过现有坐标和目的坐标计算需要走的距离，包含正负
    y_distance = coordinate_target - coordinate_now
    y_target = round(current_coordinates_y + y_distance, 1)        # 计算目标y轴的坐标,round避免往返运算的极小数
    # 判断目标y轴的坐标是否在允许范围内
    if Y_RANGE[0] <= y_target <= Y_RANGE[1]:
        print("86:目前y坐标：%s,位移量：%s" % (coordinate_now, y_distance))
        # 添加脉冲宽度判断
        if pulse_width:
            step_num, unit_step = y.move(y_distance, pulse_width)
        else:
            step_num, unit_step = y.move(y_distance)
        # 更新Y轴坐标
        y_distance_mm = round(step_num * unit_step, RECORD_DECIMALS)            # 计算出实际位移量mm
        current_coordinates_y += y_distance_mm                                  # 更新Y轴现有位置
        current_coordinates_y = round(current_coordinates_y, RECORD_DECIMALS)   # 限定小数点后8位
        current_coordinates.record('motor_y', current_coordinates_y)            # 执行更新记录
        print("96:更新后y坐标：%s" % current_coordinates_y)
    else:
        print("98:y轴运动将超出安全范围[%s, %s]，禁止此次运动" % (Y_RANGE[0], Y_RANGE[1]))
    return


# ############################### 函数说明 ###############################
# only_x函数接收目标坐标,并更新坐标位置
# 控制x轴运动
# ########################################################################
def only_x(coordinate_now, coordinate_target, pulse_width=None):
    current_coordinates_x = current_coordinates.get('motor_x')              # 获取目前主体的坐标
    # 通过现有坐标和目的坐标计算需要走的距离，包含正负
    x_distance = coordinate_target - coordinate_now
    x_target = round(current_coordinates_x + x_distance, 1)               # 计算目标x轴的坐标,round避免往返运算的极小数
    # 判断目标x轴的坐标是否在允许范围内
    if X_RANGE[0] <= x_target <= X_RANGE[1]:
        print("110:目前x坐标：%s,位移量：%s" % (coordinate_now, x_distance))
        # 添加脉冲宽度判断
        if pulse_width:
            step_num, unit_step = x.move(x_distance, pulse_width)
        else:
            step_num, unit_step = x.move(x_distance)
        # 更新X轴坐标
        x_distance_mm = round(step_num * unit_step, RECORD_DECIMALS)            # 计算出实际位移量mm
        current_coordinates_x += x_distance_mm                                  # 更新X轴现有位置
        current_coordinates_x = round(current_coordinates_x, RECORD_DECIMALS)   # 限定小数点后8位
        current_coordinates.record('motor_x', current_coordinates_x)            # 执行更新记录
        print("121:更新后x坐标：%s" % current_coordinates_x)
    else:
        print("123:x轴运动将超出安全范围[%s, %s]，禁止此次运动" % (X_RANGE[0], X_RANGE[1]))
    return
    # else:
    #     print("go脚本中X轴单独行走更新坐标出错，文件记录坐标与接收到的不符，


# ############################### 函数说明 ###############################
# only_z函数接收目标坐标,并更新坐标位置
# 控制z轴运动
# ########################################################################
def only_z(coordinate_now, coordinate_target, pulse_width=None):
    current_coordinates_z = current_coordinates.get('motor_z')              # 获取目前主体的坐标
    # 通过现有坐标和目的坐标计算需要走的距离，包含正负
    z_distance = coordinate_target - coordinate_now
    z_target = round(current_coordinates_z + z_distance, 1)              # 计算目标z轴的坐标,round避免往返运算的极小数
    # 判断目标z轴的坐标是否在允许范围内
    if Z_RANGE[0] <= z_target <= Z_RANGE[1]:
        print("142:目前z坐标：%s,位移量：%s" % (coordinate_now, z_distance))
        # 添加脉冲宽度判断
        if pulse_width:
            step_num, unit_step = z.move(z_distance, pulse_width)
        else:
            step_num, unit_step = z.move(z_distance)
        # 更新Z轴坐标
        z_distance_mm = round(step_num * unit_step, RECORD_DECIMALS)            # 计算出实际位移量mm
        current_coordinates_z += z_distance_mm                                  # 更新Z轴现有位置
        current_coordinates_z = round(current_coordinates_z, RECORD_DECIMALS)   # 限定小数点后8位
        current_coordinates.record('motor_z', current_coordinates_z)            # 执行更新记录
        print("152:更新后z坐标：%s" % current_coordinates_z)
    else:
        print("154:z轴运动将超出安全范围[%s, %s]，禁止此次运动" % (Z_RANGE[0], Z_RANGE[1]))
    return


def only_x1(coordinate_target, pulse_width=None):
    """
        x1轴运动，夹药装置的打开宽度

    Parameters
    ----------
    coordinate_target
        尖端两侧面的距离，与药片板宽度一样时，可以顺利拉回药片板
    pulse_width
        脉冲宽度，不指定时按照算法，否这按照指定的us
    """
    # 1、判断输入的目标宽度是否在允许范围内
    if not (X1_RANGE[0] <= coordinate_target <= X1_RANGE[1]):
        print("165:x1轴运动将超出安全范围[%s, %s]，禁止此次运动" % (X1_RANGE[0], X1_RANGE[1]))
        return
    current_coordinates_x1 = current_coordinates.get('motor_x1')  # 获取目前主体的坐标
    # 2、通过现有坐标和目的坐标计算需要走的距离，包含正负
    x1_distance = coordinate_target - current_coordinates_x1
    print("170:目前x1宽度为：%s,位移量：%s" % (current_coordinates_x1, x1_distance))
    # 3、判断速度模式
    #       指定了脉冲宽度即为恒速
    #       否者按默认的速度运行，有加减速过程
    if pulse_width:
        step_num, unit_step = x1.move(x1_distance, pulse_width)
    else:
        step_num, unit_step = x1.move(x1_distance)
    # 4、更新x1轴坐标
    x1_distance_mm = round(step_num * unit_step, RECORD_DECIMALS)               # 计算出实际位移量mm
    current_coordinates_x1 += x1_distance_mm                                    # 更新x1轴现有位置
    current_coordinates_x1 = round(current_coordinates_x1, RECORD_DECIMALS)     # 限定小数点后8位
    current_coordinates.record('motor_x1', current_coordinates_x1)              # 执行更新记录
    print("182:更新后x1宽度：%s" % current_coordinates_x1)
    return


# ############################### 函数说明 ###############################
# only_y1函数接收目标坐标,并更新坐标位置
# 控制y1轴运动
# ########################################################################
def only_y1(coordinate_now, coordinate_target, pulse_width=None):
    """
        y1轴运动，夹药装置的伸出与缩进

    Parameters
    ----------
    coordinate_now
        关注点当前坐标
    coordinate_target
        关注点目标坐标
    pulse_width
        脉冲宽度，不指定时按照算法，否这按照指定的us
    """
    current_coordinates_y1 = current_coordinates.get('motor_y1')  # 获取目前主体的坐标
    # 通过现有坐标和目的坐标计算需要走的距离，包含正负
    y1_distance = coordinate_target - coordinate_now
    y1_target = round(current_coordinates_y1 + y1_distance, 1)             # 计算目标z轴的坐标,round避免往返运算的极小数
    # print(y1_target)
    # 判断目标z轴的坐标是否在允许范围内
    if Y1_RANGE[0] <= y1_target <= Y1_RANGE[1]:
        print("197:目前y1坐标为：%s,位移量：%s" % (current_coordinates_y1, y1_distance))
        # 添加脉冲宽度判断
        if pulse_width:
            step_num, unit_step = y1.move(y1_distance, pulse_width)
        else:
            step_num, unit_step = y1.move(y1_distance)
        # 更新y1轴坐标
        y1_distance_mm = round(step_num * unit_step, 8)                     # 计算出实际位移量mm
        print(y1_distance_mm, current_coordinates_y1)
        current_coordinates_y1 += y1_distance_mm                            # 更新y1轴现有位置
        current_coordinates_y1 = round(current_coordinates_y1, 8)           # 限定小数点后8位
        current_coordinates.record('motor_y1', current_coordinates_y1)      # 执行更新记录
        print("207:更新后y1坐标：%s" % current_coordinates_y1)
    else:
        print("209:y1轴运动将超出安全范围[%s, %s]，禁止此次运动" % (Y1_RANGE[0], Y1_RANGE[1]))
    return


# ############################### 函数说明 ###############################
# wait函数实现去到指定等待工作的位置坐标处
# ########################################################################
def wait():
    # f = open(constant_coordinates_file_path)                            # 打开记录固定坐标的json文件
    # constant_coordinates = json.load(f)                                 # 加载文件中所用内容
    # f.close()                                                           # 关闭文件
    # 获取目前主体的坐标
    current_coordinates_x = current_coordinates.get('motor_x')
    current_coordinates_y = current_coordinates.get('motor_y')
    current_coordinates_z = current_coordinates.get('motor_z')
    target_coordinates_xyz = constant_coordinates.get("motor", "waiting_point")      # 获取等待点的坐标
    print("目前坐标：[%s, %s, %s]，等待工作点坐标：%s"
          % (current_coordinates_x, current_coordinates_y, current_coordinates_z, target_coordinates_xyz))
    only_y(current_coordinates_y, target_coordinates_xyz[1])            # Y轴运动
    only_x(current_coordinates_x, target_coordinates_xyz[0])            # X轴运动
    only_z(current_coordinates_z, target_coordinates_xyz[2])            # Z轴运动


# ############################### 函数说明 ###############################
# check_ready函数实现去到指定等待工作的位置坐标处
# ########################################################################
def check_ready():
    # f = open(constant_coordinates_file_path)                            # 打开记录固定坐标的json文件
    # constant_coordinates = json.load(f)                                 # 加载文件中所用内容
    # f.close()                                                           # 关闭文件
    # 获取目前主体的坐标
    current_coordinates_x = current_coordinates.get('motor_x')
    current_coordinates_y = current_coordinates.get('motor_y')
    current_coordinates_z = current_coordinates.get('motor_z')
    target_coordinates_xyz = constant_coordinates.get("motor", "ready_check_point")      # 获取准备原点检测的坐标
    print("目前坐标：[%s, %s, %s]，准备原点检测坐标：%s"
          % (current_coordinates_x, current_coordinates_y, current_coordinates_z, target_coordinates_xyz))
    only_y(current_coordinates_y, target_coordinates_xyz[1])  # Y轴运动
    only_x(current_coordinates_x, target_coordinates_xyz[0])  # X轴运动
    only_z(current_coordinates_z, target_coordinates_xyz[2])  # Z轴运动


# 初始化xyz轴底层驱动
def setup():
    z_setup_return = z.setup()
    if not z_setup_return:
        print('Z轴初始化失败')

    x_setup_return = x.setup()
    if not x_setup_return:
        print('X轴初始化失败')

    y_setup_return = y.setup()
    if not y_setup_return:
        print('Y轴初始化失败')

    x1_setup_return = x1.setup()
    if not x1_setup_return:
        print('X1轴初始化失败')

    y1_setup_return = y1.setup()
    if not y1_setup_return:
        print('Y1轴初始化失败')
    return True


# 循环部分
def loop():
    while True:
        only_x1(29)
        print("暂停")
        time.sleep(2)
        only_x1(30)
        print("暂停")
        time.sleep(2)
        only_x1(65)
        print("暂停")
        time.sleep(2)

    # only_x(0, 80)
    # print("暂停")
    # time.sleep(2)
    # only_x(80, 0, pw)
    # print("暂停")
    # time.sleep(2)

        # 原点定为361.7
        # only_x(361.6, 4000)
        # print("暂停")
        # time.sleep(2)
        #
        # only_x(361.8, 4000)
        # print("暂停")
        # time.sleep(2)
        #
        # i = 0
        # while i < 5:
        #     i = i + 1
        #     only_x((361.7-i*0.2), 4000)
        #     print("暂停")
        #     time.sleep(2)
        #     #
        #     # only_x((361.7+i*0.2), 4000)
        #     # print("暂停")
        #     # time.sleep(2)
        #
        # only_x(361.7, 4000)
        # print("暂停")
        # time.sleep(2)

        # return


# 结束释放
def destroy():
    z.destroy()
    y.destroy()
    x.destroy()
    return


# 如果该程序为主程序，程序在此开始运行，若不是不运行，该文件只做函数定义
if __name__ == '__main__':  # Program start from here
    setup_return = setup()
    if setup_return:
        print('始化成功')
    try:
        loop()
    except KeyboardInterrupt:  # 当按下 'Ctrl+C', 子函数 destroy()将会运行，用于停止退出
        print("程序已停止退出...")
        destroy()
