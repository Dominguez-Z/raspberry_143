#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  press_medicine_capsule.py
#      Author:  钟东佐
#        Date:  2020/05/21
#    describe:  控制药板从等待点进行压药
#########################################################
import motor.x_drive as x
import motor.y_drive as z
import motor.z_drive as y
import motor.go as go
import time


##########################################################################
# 全局常数值设定区域
PULSE_WIDTH_PRESS = 750                     # 压药脉冲间隔，控制速度
Y_DISTANCE_PRESS = 18                		# 压药y轴上升的距离
X_DISTANCE_MEDICINE_INTERVAL = 24.84          # 药之间的距离
X_DISTANCE_ORIGIN_2_MEDICINE_L1 = 64.68		# 原点到第一列药的距离
##########################################################################
# z轴关键点坐标，单位mm


##########################################################################
# ############################### 函数说明 ###############################
# medicine 函数输入代取药的坐标,移动到该位置进行割药压药
# ########################################################################
def medicine(l_num):
    # ############################ 常数值设定区域 ############################
    SLEEP_DELAY = 0.1
    PRESS_DELAY = 1
    x_distance_origin_2_medicine_l1 = X_DISTANCE_ORIGIN_2_MEDICINE_L1
    x_distance_medicine_interval = X_DISTANCE_MEDICINE_INTERVAL
    x_distance_back = 0
    # ########################################################################
    x_distance_origin_2_medicine_l_num = x_distance_origin_2_medicine_l1 + \
                                         x_distance_medicine_interval*(l_num - 1)
    x.move(x_distance_origin_2_medicine_l_num)
    x_distance_back += x_distance_origin_2_medicine_l_num
    time.sleep(SLEEP_DELAY)

    y.move(Y_DISTANCE_PRESS, PULSE_WIDTH_PRESS)
    time.sleep(PRESS_DELAY)
    y.move(-Y_DISTANCE_PRESS, PULSE_WIDTH_PRESS)
    time.sleep(SLEEP_DELAY)

    x_distance_back = -x_distance_back
    x.move(x_distance_back)
    time.sleep(SLEEP_DELAY)

# 初始化设定
def setup():
    return True


# 循环部分
def main():
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
        main()
    except KeyboardInterrupt:  # 当按下 'Ctrl+C', 子函数 destroy()将会运行，用于停止退出
        print("程序已停止退出...")
        destroy()
