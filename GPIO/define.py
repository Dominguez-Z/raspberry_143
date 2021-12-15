#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  define.py
#      Author:  钟东佐
#       Date        ||      describe
#   2021/11/16      ||  增加传感器输入的接口定义
#########################################################
"""
该模块主要是定义树莓派在硬件接口中的，输入输出接了什么硬件
按照GPIO电路板的版本更新。
"""

# ============== BCM码 ===============
# # =============== 1.2.2111版本 ============
# # 输入
# INPUT_MOTOR_ORIGIN = 11
# INPUT_MOTOR_LIMIT = 19
# INPUT_MOTOR_DRIVE_ALM = 26
#
# # 输出
# # 电机驱动，PUL脉冲，DIR方向
# MOTOR_X_PUL = 17
# MOTOR_X_DIR = 4
# MOTOR_Y_PUL = 8
# MOTOR_Y_DIR = 7
# MOTOR_Z_PUL = 20
# MOTOR_Z_DIR = 21
# MOTOR_X1_PUL = 14
# MOTOR_X1_DIR = 15
# MOTOR_Y1_PUL = 24
# MOTOR_Y1_DIR = 25
# MOTOR_L_PUL = 9
# MOTOR_L_DIR = 10
# MOTOR_R_PUL = 22
# MOTOR_R_DIR = 27
#
# LED_WS2812 = 18             # PWM控制的WS2812灯带接口
# HARDWARE_STOP_EN = 23       # 极限或者故障信号硬件逻辑停机使能端
#
# # MCP23017，i2c拓展io芯片，A0~7 + B0~7 ==> 1~8 + 9~16
# MCP23017_BM_PUSH = 1        # 摇药中推出药物的电磁铁
# # 对药板进行打药的电磁铁，跟从x轴正方向以0开始依次标号
# MCP23017_BM_HIT_0 = 2
# MCP23017_BM_HIT_1 = 3
#
# # PCA9685，i2c控制PWM芯片，一共16个控制位，0~15
# # SERVO，舵机
# PCA9685_SERVO_1 = 8         # 药兜四个暂存格掉落控制，1号门
# PCA9685_SERVO_2 = 9         # 同上，2号门
# PCA9685_SERVO_4 = 10        # 四个暂存格同时释放掉落药物
# PCA9685_SERVO_L = 12        # 切药平台的左中右三个舵机
# PCA9685_SERVO_M = 13        # 面对分药机，左手边为L
# PCA9685_SERVO_R = 14
# # LED_CAMERA，摄像头补光灯
# PCA9685_LED_1 = 0           # 摄像头1和2的补光灯
# PCA9685_LED_3 = 1           # # 摄像头3的补光灯


# =============== 1.1.0000版本 ============
# 输入
INPUT_MOTOR_ORIGIN = 20
INPUT_ERROR = 21
INPUT_Y1_LIMIT = 15

# 输出
# 电机驱动，PUL脉冲，DIR方向
MOTOR_X_PUL = 19
MOTOR_X_DIR = 26
MOTOR_Y_PUL = 8
MOTOR_Y_DIR = 7
MOTOR_Z_PUL = 11
MOTOR_Z_DIR = 16
MOTOR_X1_PUL = 10
MOTOR_X1_DIR = 9
MOTOR_Y1_PUL = 27
MOTOR_Y1_DIR = 22
MOTOR_M_PUL = 2
MOTOR_M_DIR = 3

# LED_WS2812 = 18             # PWM控制的WS2812灯带接口

BM_PUSH = 23         # 摇药中推出药物的电磁铁
BM_HIT = 18         # 对药板进行打药的电磁铁

SERVO = 24



def setup():
    """
    初始化设定
    """

    return True


def main():
    """
    主函数
    """
    while True:
        return


def destroy():
    """
    结束释放
    """
    return


if __name__ == '__main__':  # 程序从这开始
    """
    如果该程序为主程序，程序在此开始运行，若不是不运行，该文件只做函数定义
    """
    # 初始化
    setup_return = setup()
    if setup_return:
        print('始化成功')

    try:
        main()
    except KeyboardInterrupt:  # 当按下 'Ctrl+C', 子函数 destroy()将会运行，用于停止退出
        print("程序已停止退出...")
        destroy()
 