#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  ark_barrels.py
#      Author:  钟东佐
#        Date:  2020/5/13
#    describe:  用于开机后测试所有药柜桶位置是否正确，
#               同时测试了xyz轴是否正常工作
#########################################################
import JSON.coordinate_converter as coordinate_converter
import JSON.ark_barrels_coordinates as ark_barrels_coordinates
import motor.go as go
# ############################ 常数值设定区域 ############################

# ########################################################################


# ############################### 函数说明 ###############################
# 调用运行将实现走一遍柜桶所在位置确保xyz轴工作正常且柜桶位置正确
# ########################################################################
def run_all():
    ark_barrels_all = ark_barrels_coordinates.get_all()                     # 获取柜桶坐标文件中所用内容
    ark_barrels_sum = len(ark_barrels_all)                                  # 得出柜桶总数，用于控制遍历柜桶
    ark_barrels_keys = list(ark_barrels_all.keys())                         # 获取所有key作为列表
    print(ark_barrels_sum)
    for i in range(ark_barrels_sum):                                        # 循环走一遍所有柜桶
        target_coordinates_xyz = ark_barrels_all[ark_barrels_keys[i]]               # 获取目标柜桶的坐标
        # 获取目前主体的坐标
        current_coordinates_body = coordinate_converter.body_cusp_center()
        print("前往%s号柜桶，该柜桶坐标为%s，目前body所在坐标为%s"
              % (ark_barrels_keys[i], target_coordinates_xyz, current_coordinates_body))     # 打印相关信息
        go.only_y(current_coordinates_body[1], target_coordinates_xyz[1])            # Y轴运动
        go.only_x(current_coordinates_body[0], target_coordinates_xyz[0])            # X轴运动
        # Z轴做一个往返动作，意指顺利进入拿药位置
        go.only_z(current_coordinates_body[2], target_coordinates_xyz[2])
        go.only_z(target_coordinates_xyz[2], current_coordinates_body[2])
        print("body的坐标更新为：%s" % coordinate_converter.body_cusp_center())         # 打印信息
    go.wait()                                                               # 检查结束后去工作等待点
    return 'success'


# ############################### 函数说明 ###############################
# 调用走指定柜桶拿药拍照检测
# ########################################################################
def camera():
    return


# 初始化设定
def setup():
    return True


# 循环部分
def loop():
    while True:
        run_all()
        return


# 结束释放
def destroy():
    return


# 如果该程序为主程序，程序在此开始运行，若不是不运行，该文件只做函数定义
if __name__ == '__main__':                  # Program start from here
    setup_return = setup()
    if setup_return:
        print('始化成功')
    try:
        loop()
    except KeyboardInterrupt:               # 当按下 'Ctrl+C', 子函数 destroy()将会运行，用于停止退出
        print("程序已停止退出...")
        destroy()
