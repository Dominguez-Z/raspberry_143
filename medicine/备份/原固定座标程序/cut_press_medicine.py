#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  cut_press_medicine.py
#      Author:  钟东佐
#        Date:  2020/05/05
#    describe:  控制药板从等待点进行割药和压药
#########################################################
import motor.x_drive as x
import motor.y_drive as z
import motor.z_drive as y
import motor.go as go
import time


##########################################################################
# 全局常数值设定区域
Y_DISTANCE_CUT = -14.5                 # 割药y轴下降的距离
Y_DISTANCE_PRESS = 26                		# 压药y轴上升的距离
X_DISTANCE_CUT_2_PRESS = -24.5      		# 割药点和压药点之间距离，符号代表2前面的坐标位于后面的右边
X_DISTANCE_MEDICINE_INTERVAL = 12.9          # 药之间的距离
X_DISTANCE_ORIGIN_2_MEDICINE_L1 = 97.9		# 原点到第一列药的距离
##########################################################################
# z轴关键点坐标，单位mm


##########################################################################
# ############################### 函数说明 ###############################
# medicine 函数输入代取药的坐标,移动到该位置进行割药压药
# ########################################################################
def medicine(l_num):
    # ############################ 常数值设定区域 ############################
    SLEEP_DELAY = 0.1
    CUT_PRESS_DELAY = 1
    x_distance_origin_2_medicine_l1 = X_DISTANCE_ORIGIN_2_MEDICINE_L1
    x_distance_medicine_interval = X_DISTANCE_MEDICINE_INTERVAL
    # ########################################################################
    x_distance_origin_2_medicine_l_num = x_distance_origin_2_medicine_l1 + \
                                         x_distance_medicine_interval*(l_num - 1)
    x.move(x_distance_origin_2_medicine_l_num)
    time.sleep(SLEEP_DELAY)

    y.move(Y_DISTANCE_CUT)
    time.sleep(CUT_PRESS_DELAY)
    y.move(-Y_DISTANCE_CUT)
    time.sleep(SLEEP_DELAY)
    x.move(X_DISTANCE_CUT_2_PRESS)
    time.sleep(SLEEP_DELAY)

    y.move(Y_DISTANCE_PRESS)
    time.sleep(CUT_PRESS_DELAY)
    y.move(-Y_DISTANCE_PRESS)
    time.sleep(SLEEP_DELAY)
    x.move(-(x_distance_origin_2_medicine_l_num + X_DISTANCE_CUT_2_PRESS))
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
