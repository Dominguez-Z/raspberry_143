#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  take_medicine.py
#      Author:  钟东佐
#        Date:  2020/04/07
#    describe:  控制从割药附近作为原点到达药弹夹处拿取药片板的，并回到原点
#########################################################
import motor.x_drive as x
import motor.y_drive as z
import motor.z_drive as y
import motor.go as go
import time


##########################################################################
# 全局常数值设定区域
XY_POSITION_BEGIN = (-464.6, 0)
XY_POSITION_POLE_INOUT = (-102.2, 371)
XY_POSITION_PLATE_INOUT = (-102.2, 366)
XY_POSITION_ORIGIN = (0, 0)
##########################################################################
# z轴关键点坐标，单位mm
Z_POSITION_START = 11.9                # z轴机械起始点的位置
Z_POSITION_ORIGIN = 0                   # z轴坐标原点，初定于拿到药片板移动到最后的位置
Z_POSITION_TAKE = 156.4 - 1.5                   # z轴拿药片板的位置坐标，1.5是吸附磁铁螺丝的厚度
Z_DISTANCE_BACK_ORIGIN = 1              # 当带有药片夹时，回程到原点增加这段距离使得原点处机械结构卡死稳固
##########################################################################


# ///////////////////////////////////////////////////////////////////////////      z轴运动控制
# ############################### 函数说明 ###############################
# z轴 开始位置移动的到原点
##########################################################################
def z_start_2_origin(dir_change_state='change_dir'):
    start = Z_POSITION_START
    origin = Z_POSITION_ORIGIN
    z.move(origin - start, dir_change_state)


# ############################### 函数说明 ###############################
# z轴 原点移动的到开始位置
##########################################################################
def z_origin_2_start(dir_change_state='change_dir'):
    start = Z_POSITION_START
    origin = Z_POSITION_ORIGIN
    z.move(start - origin, dir_change_state)


# ############################### 函数说明 ###############################
# z轴 原点到拿药点
##########################################################################
def z_origin_2_take(dir_change_state='change_dir'):
    take = Z_POSITION_TAKE
    origin = Z_POSITION_ORIGIN
    z.move(take - origin, dir_change_state)


# ############################### 函数说明 ###############################
# z轴 拿药点到原点
##########################################################################
def z_take_2_origin(dir_change_state='change_dir'):
    take = Z_POSITION_TAKE
    origin = Z_POSITION_ORIGIN
    z.move(origin - take, dir_change_state)
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


SLEEP_DELAY = 0.5
def medicine_give():
    # 从开始去拿药点拿药
    go.xy(XY_POSITION_BEGIN, XY_POSITION_POLE_INOUT)
    time.sleep(SLEEP_DELAY)
    # z轴进拿药位
    z_origin_2_take('change_dir')
    time.sleep(SLEEP_DELAY)
    go.only_y(XY_POSITION_POLE_INOUT[1], XY_POSITION_PLATE_INOUT[1])
    time.sleep(SLEEP_DELAY)
    # z轴拿药出来
    z_take_2_origin('change_dir')
    time.sleep(SLEEP_DELAY)
    # 拿药点到割药原点
    go.xy(XY_POSITION_PLATE_INOUT, XY_POSITION_ORIGIN)
    time.sleep(SLEEP_DELAY)

def medicine_back():
    # 割药原点回放药点
    go.xy(XY_POSITION_ORIGIN, XY_POSITION_PLATE_INOUT)
    time.sleep(SLEEP_DELAY)
    # z轴进拿药位
    z_origin_2_take('change_dir')
    time.sleep(SLEEP_DELAY)
    # y轴上升离开扣点
    go.only_y(XY_POSITION_PLATE_INOUT[1], XY_POSITION_POLE_INOUT[1])
    time.sleep(SLEEP_DELAY)
    # z轴出来
    z_take_2_origin('change_dir')
    time.sleep(SLEEP_DELAY)
    # 放完药回原点
    go.xy(XY_POSITION_POLE_INOUT, XY_POSITION_BEGIN)
    time.sleep(SLEEP_DELAY)



# 初始化设定
def setup():
    return True


# 循环部分
def loop():
    while True:
        return


# 结束释放
def destroy():
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
