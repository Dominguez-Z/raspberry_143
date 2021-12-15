#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  xz_control.py
#      Author:  钟东佐
#        Date:  2020/03/25
#    describe:  调用x、z轴底层驱动，控制xz平面的运动，例如割药
#########################################################
import motor.y_drive as z
import motor.x_drive as x
import time


# 用于控制运动方向
# X_LEFT = 1
# X_RIGHT = 0


# 函数的初始化操作，主要包含各模块的初始化setup
def setup():
    z_setup_return = z.setup()
    if not z_setup_return:
        print('z轴初始化失败')

    x_setup_return = x.setup()
    if not x_setup_return:
        print('x轴初始化失败')

    return True


# 圆型药方形割


# xz控制测试，距离单位为mm
def move_test():

    print("X轴向右")
    x.move('x_right', 11)
    time.sleep(1)

    print("Z轴向后")
    z.move('z_backward', 'no_change_dir', 11)
    time.sleep(1)

    print("X轴向左")
    x.move('x_left', 11)
    time.sleep(1)

    print("Z轴向前")
    z.move('z_forward', 'no_change_dir', 11)
    print("stop...")

    time.sleep(3)

    '''
    print("Z轴向后")
    z.move('z_backward', 'no_change_dir', 5)
    print("stop...")
    time.sleep(5)
    '''


# 函数循环
def loop():
    while True:
        x.move('x_right', 80)


# 退出程序前的关闭操作
def destroy():
    z.destroy()
    x.destroy()


# 如果该程序为主程序，程序在此开始运行，若不是不运行，该文件只做函数定义
if __name__ == '__main__':
    setup_return = setup()
    if not setup_return:
        print('xz控制程序初始化失败')

    try:
        loop()

    except KeyboardInterrupt:  # 当按下 'Ctrl+C', 子函数 destroy()将会运行，用于停止退出
        print("xz控制程序退出")
        destroy()
