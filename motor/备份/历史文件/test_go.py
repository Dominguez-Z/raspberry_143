#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  test_go.py
#      Author:  钟东佐
#        Date:  2020/11/20
#    describe:  XYZ控制的底层代码封装，调用运动结束会更新坐标到JSON/constant_coordinates.json中
#               该测试文档用于正式文档前的分不测试
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
# 夹取药片板的函数，只做夹板动作
# ########################################################################
def y_y1(distance):
    # 创建x、y轴子线程
    threads = []
    t1 = threading.Thread(target=y.move, args=(distance,1680))
    threads.append(t1)
    t2 = threading.Thread(target=y1.move, args=(-distance,500))
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
        time.sleep(3)
        go_state = y_y1(6)
        if go_state == 'go_y_y1_success':
            pass
        else:
            return
        time.sleep(1)
        go_state = y_y1(-6)
        if go_state == 'go_y_y1_success':
            pass
        else:
            return
        # time.sleep(3)

        # return


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
