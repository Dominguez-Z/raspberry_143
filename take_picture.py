#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  take_picture.py
#      Author:  钟东佐
#        Date:  2020/12/22
#    describe:  拍照测试图像识别
#########################################################
import JSON.current_coordinates as current_coordinates
import camera.camera_0 as camera
import electromagnet.strike_drug_drive as strike_drug
import motor.y_drive as y
import motor.x_drive as x
import motor.z_drive as z
import motor.y1_drive as y1
import motor.x1_drive as x1
import motor.go as go
import motor.reset as check
# import  medicine.press_medicine_capsule as press_medicine_capsule
# import medicine.take_medicine as take
import time
# ############################ 常数值设定区域 ############################

# ########################################################################


# 主函数的初始化操作，主要包含各模块的初始化setup
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

    x1_setup_return = x1.setup()
    if not x1_setup_return:
        print('X1轴初始化失败')

    y1_setup_return = y1.setup()
    if not y1_setup_return:
        print('Y1轴初始化失败')

    strike_drug_setup_return = strike_drug.setup()
    if not strike_drug_setup_return:
        print('打药继电器初始化失败')

    x_check_setup_return = check.setup()
    if not x_check_setup_return:
        print('xyz轴红外检测初始化失败')

    return True


# 主函数循环
def main():
    # 先拍一张启动相机，该照片需丢弃
    camera.take_photo()
    time.sleep(0.5)
    # 获取电机的x坐标作为原点基础
    # origin_coordinates_x = current_coordinates.get('motor_x')
    origin_coordinates_x = 600

    # 获取目前x坐标
    current_coordinates_x = current_coordinates.get('motor_x')
    # 根据原点计算目前x目标坐标
    target_coordinates_x = origin_coordinates_x
    print("目前x坐标：[%s]，目标点坐标：%s"
          % (current_coordinates_x, target_coordinates_x))
    # 回原点
    go.only_x(current_coordinates_x, target_coordinates_x, 2000)  # X轴运动
    time.sleep(0.2)

    # 左偏移拍照循环
    for i in range(50):
        number = i * 0.05
        # 获取目前x坐标
        current_coordinates_x = current_coordinates.get('motor_x')
        # 根据原点计算目前x目标坐标
        target_coordinates_x = origin_coordinates_x - number
        print("目前x坐标：[%s]，目标点坐标：%s"
              % (current_coordinates_x, target_coordinates_x))
        go.only_x(current_coordinates_x, target_coordinates_x, 2000)      # X轴运动
        for j in range(5):
            picture_name = "L_" + str("%.2f"%number) + "_" + str(j)
            print(picture_name)
            # 拍照
            camera.take_photo(picture_name)
            time.sleep(0.2)

    # 获取目前x坐标
    current_coordinates_x = current_coordinates.get('motor_x')
    # 根据原点计算目前x目标坐标
    target_coordinates_x = origin_coordinates_x
    print("目前x坐标：[%s]，目标点坐标：%s"
          % (current_coordinates_x, target_coordinates_x))
    # 回原点
    go.only_x(current_coordinates_x, target_coordinates_x, 2000)  # X轴运动
    time.sleep(0.2)

    for i in range(50):
        number = i * 0.05
        # 获取目前x坐标
        current_coordinates_x = current_coordinates.get('motor_x')
        # 根据原点计算目前x目标坐标
        target_coordinates_x = origin_coordinates_x + number
        print("目前x坐标：[%s]，目标点坐标：%s"
              % (current_coordinates_x, target_coordinates_x))
        go.only_x(current_coordinates_x, target_coordinates_x, 2000)  # X轴运动
        for j in range(5):
            picture_name = "R_" + str("%.2f" % number) + "_" + str(j)
            print(picture_name)
            # 拍照
            camera.take_photo(picture_name)
            time.sleep(0.2)
    return


# 退出程序前的关闭操作
def destroy():
    z.destroy()
    y.destroy()
    x.destroy()
    check.destroy()


# 如果该程序为主程序，程序在此开始运行，若不是不运行，该文件只做函数定义
if __name__ == '__main__':
    main_setup_return = setup()
    if not main_setup_return:
        print('主函数初始化失败')

    try:
        main()

    except KeyboardInterrupt:  # 当按下 'Ctrl+C', 子函数 destroy()将会运行，用于停止退出
        print("主函数退出")
        destroy()
