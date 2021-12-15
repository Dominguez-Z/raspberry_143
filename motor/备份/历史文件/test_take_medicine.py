#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  test_take_medicine.py
#      Author:  钟东佐
#        Date:  2020/11/24
#    describe:  测试拿药动作
#
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
import threading

# ############################ 常数值设定区域 ############################
current_path = os.path.dirname(__file__)            # 获取本文件的路径
constant_coordinates_file_path = current_path + "/../JSON/constant_coordinates.json"   # 加上目标文件的相对路径
# 用于指定坐标[x,y,z]中，切片时指定哪一位
# X = 0
# Y = 1
# Z = 2
# ########################################################################
# CUT_WAIT_COORDINATE_XY =[0, 0]  # xy待切割点坐标


# ############################### 函数说明 ###############################
# y轴和y1轴同步运动实现夹取点保持不动，上下夹片收紧夹稳药片板
# ########################################################################
def y_y1(distance):
    # 创建x、y轴子线程
    threads = []
    t1 = threading.Thread(target=y.move, args=(distance,3360))
    threads.append(t1)
    t2 = threading.Thread(target=y1.move, args=(-distance,1000))
    threads.append(t2)
    # 将所有子线程开始
    for t in threads:
        t.setDaemon(True)
        t.start()
    # 打开子线程的阻塞保证所有子线程都运行完了，主线程才继续
    for t in threads:
        t.join()
        # print("threads : %s.time is: %s" % (t, ctime()))
    print('go_y_y1_success')
    return 'go_y_y1_success'


# ############################### 函数说明 ###############################
# do_take()
# ########################################################################
def do_take():
    sleep_time = 1
    # z.move(0.5)
    # y1.move(5, 1000)


    # 收回
    # y1.move(80, 1000)
    # time.sleep(sleep_time)
    # y1.move(5, 2000)
    # time.sleep(sleep_time)
    # y_y1(-5.5)
    # time.sleep(sleep_time)
    # y.move(-4.7, 1000)
    # time.sleep(sleep_time)
    # z.move(-3.35, 1000)
    # time.sleep(sleep_time)
    # y.move(-93.5)
    # time.sleep(sleep_time)
    # z.move(-148.25)
    # time.sleep(sleep_time)

    # 前提是X轴已经对准，z轴上升到前端二铁片位于最底药板之上，目前测量距离为  mm
    z.move(149)
    time.sleep(sleep_time)
    # Y轴前进到达对准位判断位置是否正确
    y.move(74.6)
    time.sleep(sleep_time)
    # Y轴运动将铁片插入最下药板和上一片药板之间，然后Z轴提高至药板槽与药板卡位相平的位置
    y.move(18.5, 1000)
    time.sleep(sleep_time)
    z.move(3.6, 2000)
    time.sleep(sleep_time)
    # Y轴进一步插入，使得药片板位于夹片之间准备夹取
    y.move(4.7, 1000)
    time.sleep(sleep_time)
    # Z轴降低使得药片刚好高于卡位
    z.move(-1.5, 2000)
    time.sleep(sleep_time)
    # Y轴和Y1轴慢速反向运动，把拉钩拉入药板槽，加紧药板
    y_y1(5.5)
    time.sleep(sleep_time)
    # 此时y轴已到最前无法向前，但是y1轴可能还没有夹稳，增加一段使得确保夹稳
    y1.move(-5, 2000)
    time.sleep(sleep_time)
    # Y1轴持续拉回，将夹紧的药板完全拉入药板槽
    y1.move(-82,1000)
    time.sleep(sleep_time)
    # Z下降至插入前的位置
    z.move(-2.1, 2000)
    time.sleep(sleep_time)
    # Y轴完全拉出，恢复到起始位置
    back_l = -(79.6 + 13.5 + 4.7)
    y.move(back_l)
    y.move_step(-1, 3000)        # 经过计算前面的行程会有1步的误差，返回时补上
    time.sleep(sleep_time)
    # Z轴下降至起始位置
    z.move(-149)
    time.sleep(sleep_time)

    return


# ############################### 函数说明 ###############################
# do_back()
# ########################################################################
def do_back():
    sleep_time = 1
    # z.move(-149)
    # time.sleep(sleep_time)
    # 前提是X轴已经对准，z轴上升到前端二铁片位于最底药板之下，目前测量距离为  mm
    z.move(145)
    time.sleep(sleep_time)
    # Y轴前进到达对准位判断位置是否正确
    y.move(75.6)
    time.sleep(sleep_time)
    # Y轴运动将铁片插入最下药板之下，然后Z轴提高至药板槽与药板卡位相平的位置
    y.move(6.5, 1000)
    time.sleep(sleep_time)
    z.move(6.1, 2000)
    time.sleep(sleep_time)
    # Y轴进一步插入
    y.move(15.7, 1000)
    time.sleep(sleep_time)
    # Y1轴持续推出，将夹紧的药板完全推入存储柜
    y1.move(87, 1000)
    time.sleep(sleep_time)
    # Y轴和Y1轴慢速反向运动，放松药板
    y_y1(-5.5)
    time.sleep(sleep_time)
    # Z下降至插入前的位置
    z.move(-1.1, 2000)
    time.sleep(sleep_time)
    # Y轴完全拉出，恢复到起始位置
    back_l = -(79.6 + 13.5 + 4.7)
    y.move(back_l)
    time.sleep(sleep_time)
    # Z轴下降至起始位置
    z.move(-150)
    time.sleep(sleep_time)
    return

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

    y1_setup_return = y1.setup()
    if not y1_setup_return:
        print('Y1轴初始化失败')

    x1_setup_return = x1.setup()
    if not x1_setup_return:
        print('X1轴初始化失败')

    return True


# 循环部分
def loop():
    while True:
        do_take()
        time.sleep(3)
        do_back()
        time.sleep(3)


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
    setup_return = setup()
    if setup_return:
        print('始化成功')
    try:
        loop()
    except KeyboardInterrupt:  # 当按下 'Ctrl+C', 子函数 destroy()将会运行，用于停止退出
        print("程序已停止退出...")
        destroy()
