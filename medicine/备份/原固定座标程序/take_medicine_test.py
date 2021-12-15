#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  jump.py
#      Author:  钟东佐
#        Date:  2020/04/07
#    describe:  控制从割药附近作为原点到达药弹夹处拿取药片板的，并回到原点
#########################################################
import motor.x_drive as x
import motor.y_drive as z
import motor.z_drive as y

##########################################################################
# 全局常数值设定区域
# x轴关键点坐标或距离，单位mm
X_POSITION_CUT_ORIGIN = 540         # 割药原点，定义为割药的刀刚好触碰到药板夹的左边缘
X_DISTANCE_CUT_2_PRESS = -18.8      # 割药点和压药点之间距离，符号代表2前面的坐标位于后面的右边
X_POSITION_TAKE = 281.41            # 拿药点坐标
X_POSITION_ORIGIN = 0               # x轴坐标原点，初定于左边空白，方便y轴启动时没有遮挡
# y轴关键点坐标，单位mm
Y_DISTANCE_MIN_2_ORIGIN = 71.70     # y轴机械最低点到原点的距离
Y_POSITION_ORIGIN = 0               # y轴坐标原点，初定于割药和压药之间，主体可以没有阻挡左右移动的位置

Y_POSITION_POLE_ENTER = 370.75      # 杆子可以顺利进入药板夹之间的坐标
Y_DISTANCE_POLE_ENTER_2_TAKE = -10.1             # 杆子进入的高度与可以拉出药板夹的相差距离，符号代表2前面的坐标比后面的高
Y_DISTANCE_POLE_ENTER_2_BAKE = -6.42             # 杆子进入的高度与药板夹推回药弹夹的相差距离
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
    z.move('z_backward', dir_change_state, origin - start)


# ############################### 函数说明 ###############################
# z轴 原点移动的到开始位置
##########################################################################
def z_origin_2_start(dir_change_state='change_dir'):
    start = Z_POSITION_START
    origin = Z_POSITION_ORIGIN
    z.move('z_forward', dir_change_state, start - origin)


# ############################### 函数说明 ###############################
# z轴 原点到拿药点
##########################################################################
def z_origin_2_take(dir_change_state='change_dir'):
    take = Z_POSITION_TAKE
    origin = Z_POSITION_ORIGIN
    z.move('z_forward', dir_change_state, take - origin)


# ############################### 函数说明 ###############################
# z轴 拿药点到原点
##########################################################################
def z_take_2_origin(dir_change_state='change_dir'):
    take = Z_POSITION_TAKE
    origin = Z_POSITION_ORIGIN
    z.move('z_backward', dir_change_state, origin - take)
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


# ///////////////////////////////////////////////////////////////////////////      Y轴运动控制
# ############################### 函数说明 ###############################
# y轴机械最低点上升到原点
##########################################################################
def y_min_2_origin():
    min_2_origin = Y_DISTANCE_MIN_2_ORIGIN
    y.move('y_up', min_2_origin)


# ############################### 函数说明 ###############################
# y轴原点上升到拿药时的进杆点
##########################################################################
def y_origin_2_pole_enter():
    origin = Y_POSITION_ORIGIN
    pole_enter = Y_POSITION_POLE_ENTER
    y.move('y_up', pole_enter - origin)


# ############################### 函数说明 ###############################
# y轴拿药时的进杆点下降到原点
##########################################################################
def y_pole_enter_2_origin():
    origin = Y_POSITION_ORIGIN
    pole_enter = Y_POSITION_POLE_ENTER
    y.move('y_down', origin - pole_enter)


# ############################### 函数说明 ###############################
# y轴拿药时的进杆点下降到拉出药板夹的高度
##########################################################################
def y_pole_enter_2_take():
    pole_enter_2_take = Y_DISTANCE_POLE_ENTER_2_TAKE
    y.move('y_down', pole_enter_2_take)


# ############################### 函数说明 ###############################
# y轴拉出药板夹下降到原点位于割药水平高度
##########################################################################
def y_take_2_origin():
    origin = Y_POSITION_ORIGIN
    pole_enter = Y_POSITION_POLE_ENTER
    pole_enter_2_take = Y_DISTANCE_POLE_ENTER_2_TAKE
    y.move('y_down', origin - (pole_enter + pole_enter_2_take))


# ############################### 函数说明 ###############################
# y轴 割完药从原点上升到药板夹推回药弹夹的高度
##########################################################################
def y_origin_2_bake():
    origin = Y_POSITION_ORIGIN
    pole_enter = Y_POSITION_POLE_ENTER
    pole_enter_2_bake = Y_DISTANCE_POLE_ENTER_2_BAKE
    y.move('y_up', (pole_enter + pole_enter_2_bake) - origin)


# ############################### 函数说明 ###############################
# y轴 割完药从原点上升到药板夹推回药弹夹的高度
##########################################################################
def y_bake_2_pole_enter():
    pole_enter_2_bake = Y_DISTANCE_POLE_ENTER_2_BAKE
    y.move('y_up', -pole_enter_2_bake)
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


# ///////////////////////////////////////////////////////////////////////////      X轴运动控制
# ############################### 函数说明 ###############################
# x轴原点移动到拿药点
##########################################################################
def x_origin_2_take():
    origin = X_POSITION_ORIGIN
    take = X_POSITION_TAKE
    x.move('x_right', take - origin)


# ############################### 函数说明 ###############################
# x轴拿药点移动到原点
##########################################################################
def x_take_2_origin():
    origin = X_POSITION_ORIGIN
    take = X_POSITION_TAKE
    x.move('x_left', origin - take)


# ############################### 函数说明 ###############################
# x轴拿药点移动到割药原点
##########################################################################
def x_take_2_cut_origin():
    take = X_POSITION_TAKE
    cut_origin = X_POSITION_CUT_ORIGIN
    x.move('x_right', cut_origin - take)


# ############################### 函数说明 ###############################
# x轴割药原点移动到拿药点
##########################################################################
def x_cut_origin_2_take():
    take = X_POSITION_TAKE
    cut_origin = X_POSITION_CUT_ORIGIN
    x.move('x_left', take - cut_origin)


# ############################### 函数说明 ###############################
# x轴割药点移动到压药点
##########################################################################
def x_cut_2_press():
    cut_2_press = X_DISTANCE_CUT_2_PRESS
    x.move('x_left', cut_2_press)


# ############################### 函数说明 ###############################
# x轴压药点移动到割药点
##########################################################################
def x_press_2_cut():
    cut_2_press = X_DISTANCE_CUT_2_PRESS
    x.move('x_right', -cut_2_press)
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


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
