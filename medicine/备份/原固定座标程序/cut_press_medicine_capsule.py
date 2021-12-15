#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  cut_press_medicine_capsule.py
#      Author:  钟东佐
#        Date:  2020/05/11
#    describe:  控制药板从等待点进行割药和压药,针对药物是胶囊
#########################################################
import motor.x_drive as x
import motor.y_drive as z
import motor.z_drive as y
import motor.go as go
import time


##########################################################################
# 全局常数值设定区域
Y_DISTANCE_CUT = -14.5                      # 割药y轴下降的距离
Y_DISTANCE_PRESS = 26                		# 压药y轴上升的距离

X_DISTANCE_MEDICINE_INTERVAL = 24.84          # 药之间的距离
X_DISTANCE_ORIGIN_2_MEDICINE_L1_CUT1 = 96.85		# 原点到第一列药的第一个切割点距离
X_DISTANCE_CUT1_2_CUT2 = 19.5		        # 第一个切割点到第二个切割点距离
X_DISTANCE_CUT2_2_PRESS2 = -30.06      		        # 割药点2和压药点2之间距离
X_DISTANCE_PRESS2_2_PRESS1 = -11.95                 # 压药点2和压药点1之间距离
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
    x_distance_origin_2_medicine_l1_cut1 = X_DISTANCE_ORIGIN_2_MEDICINE_L1_CUT1
    x_distance_cut1_2_cut2 = X_DISTANCE_CUT1_2_CUT2
    x_distance_medicine_interval = X_DISTANCE_MEDICINE_INTERVAL
    x_distance_cut2_2_press2 = X_DISTANCE_CUT2_2_PRESS2
    x_distance_press2_2_press1 = X_DISTANCE_PRESS2_2_PRESS1
    x_distance_back = 0
    # ########################################################################
    x_distance_origin_2_medicine_l_num = x_distance_origin_2_medicine_l1_cut1 + \
                                         x_distance_medicine_interval*(l_num - 1)
    x.move(x_distance_origin_2_medicine_l_num)
    x_distance_back += x_distance_origin_2_medicine_l_num
    time.sleep(SLEEP_DELAY)
    # 第一切割点
    y.move(Y_DISTANCE_CUT)
    time.sleep(CUT_PRESS_DELAY)
    y.move(-Y_DISTANCE_CUT)
    time.sleep(SLEEP_DELAY)

    x.move(x_distance_cut1_2_cut2)
    x_distance_back += x_distance_cut1_2_cut2
    time.sleep(SLEEP_DELAY)
    # 第二切割点
    y.move(Y_DISTANCE_CUT)
    time.sleep(CUT_PRESS_DELAY)
    y.move(-Y_DISTANCE_CUT)
    time.sleep(SLEEP_DELAY)

    x.move(x_distance_cut2_2_press2)
    x_distance_back += x_distance_cut2_2_press2
    time.sleep(SLEEP_DELAY)
    # 第二个压药点
    y.move(Y_DISTANCE_PRESS)
    time.sleep(CUT_PRESS_DELAY)
    y.move(-Y_DISTANCE_PRESS)
    time.sleep(SLEEP_DELAY)

    x.move(x_distance_press2_2_press1)
    x_distance_back += x_distance_press2_2_press1
    time.sleep(SLEEP_DELAY)
    # 第一个压药点
    y.move(Y_DISTANCE_PRESS)
    time.sleep(CUT_PRESS_DELAY)
    y.move(-Y_DISTANCE_PRESS)
    time.sleep(SLEEP_DELAY)

    x_distance_back = -x_distance_back
    x.move(x_distance_back)
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
