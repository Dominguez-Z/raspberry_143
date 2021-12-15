#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  go.py
#      Author:  钟东佐
#        Date:  2020/4/23
#    describe:  控制xy平面和xz平面的运动，并通过多线程实现双轴同时运动
#########################################################
import time
import motor.y_drive as z
import motor.x_drive as x
import motor.z_drive as y
import threading

CUT_WAIT_COORDINATE_XY =[0, 0]  # xy待切割点坐标


# ############################### 函数说明 ###############################
# xy函数接收以列表的方式接收当前坐标[x0, y0]和目标坐标[x1, y1]
# 创建线程分别控制x、y轴运动
# ########################################################################
def xy(coordinate_now, coordinate_target):
    # 为保证目前坐标或目标坐标其一是待切割点才运行
    # 避免运动平面撞上其他东西
    cut_wait_coordinate = CUT_WAIT_COORDINATE_XY
    if coordinate_now == cut_wait_coordinate or coordinate_target == cut_wait_coordinate:
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
    else:
        print("当前坐标或者目标坐标非指定点%s，运动过程可能撞击其他部件，已停止并放回" % cut_wait_coordinate)
        return 'go_xy_error'


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
    return True


# 循环部分
def loop():
    while True:
        go_state = xy([0, 0], [-200, 200])
        if go_state == 'go_xy_success':
            pass
        else:
            return
        time.sleep(1)
        go_state = xy([-200, 200], [0, 0])
        if go_state == 'go_xy_success':
            pass
        else:
            return
        time.sleep(1)

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
