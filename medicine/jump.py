#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  jump.py
#      Author:  钟东佐
#        Date:  2020/05/28
#    describe:  去到指定的药柜点
#########################################################
import JSON.ark_barrels_coordinates as ark_barrels_coordinates
import JSON.coordinate_converter as coordinate_converter
import JSON.constant_coordinates as constant_coordinates
import motor.go as go


# ############################### 函数说明 ###############################
# 实现去到指定柜桶的XY位置,第i行第j列
# ########################################################################
def ark_barrel(i, j):
    # 获取目标柜桶的坐标
    # target_coordinates_xyz = ark_barrels_coordinates.get_ark_barrels(i, j)
    target_coordinates_xyz = ark_barrels_coordinates.get_plate(i, j)
    # 获取目前主体的坐标
    body_cusp_center = coordinate_converter.body_cusp_center()
    print("前往第%s行第%s列柜桶，该柜桶坐标为%s，目前cusp_center所在坐标为%s"
          % (i, j, target_coordinates_xyz, body_cusp_center))       # 打印相关信息
    # 运动到指定位置，xz代替分开运动的only
    # go.only_z(body_cusp_center[2], target_coordinates_xyz[2])       # Z轴运动
    # go.only_x(body_cusp_center[0], target_coordinates_xyz[0])       # X轴运动
    go.xz(
        coordinate_now_x=body_cusp_center[0],
        coordinate_target_x=target_coordinates_xyz[0],
        coordinate_now_z=body_cusp_center[2],
        coordinate_target_z=target_coordinates_xyz[2],
    )
    print("27:cusp_center的坐标更新为：%s" % coordinate_converter.body_cusp_center())             # 打印信息
    return


# ############################### 函数说明 ###############################
# 实现去到打药准备点
# ########################################################################
def strike_drug_ready():
    # 1、药夹尖端退后到打药装置最后，并有余量
    # 1.1 获取当前尖端y坐标
    body_cusp_center = coordinate_converter.body_cusp_center()          # 一次提取xyz，后续需要直接获取
    body_cusp_center_y = body_cusp_center[1]
    # 1.2 获取打药装置最后的y坐标
    the_back_strike_drug_parts = constant_coordinates.get("strike_drug_parts", "1", "the_back")
    print(body_cusp_center_y, the_back_strike_drug_parts)
    # 1.3 退后到相差20mm的位置
    go.only_y(body_cusp_center_y, (the_back_strike_drug_parts - 20), 1000)

    # 2、伸出的推杆最底部要高于打药装置最顶，并有余量
    # 2.1 获取当前推杆最底部的z坐标
    the_bottom_push_rod = coordinate_converter.body_push_rod("the_bottom")
    # 2.2 获取打药装置最顶的z坐标
    the_top_strike_drug_parts = constant_coordinates.get("strike_drug_parts", "1", "the_top")
    print(the_bottom_push_rod, the_top_strike_drug_parts)
    # 2.3 调整高度，余量10mm
    go.only_z(the_bottom_push_rod, (the_top_strike_drug_parts + 10), 2000)

    # 3、移动x轴让药片中心与打药孔中心对齐
    # 3.1 获取当前药片中心，即夹子中心x坐标
    body_cusp_center_x = body_cusp_center[0]
    # 3.2 获取打药孔x坐标
    strike_drug_parts_center = constant_coordinates.get("strike_drug_parts", "1", "center")     # 一次提取xyz坐标，后续需要直接获取
    strike_drug_parts_center_x = strike_drug_parts_center[0]
    print(body_cusp_center_x, strike_drug_parts_center_x)
    # 3.3 移动x轴对齐
    go.only_x(body_cusp_center_x, strike_drug_parts_center_x, 2000)

    # 4、降低z轴让药片底面与打药支撑面平齐，稍微高一点
    # 4.1 获取当前药片支撑面的z坐标
    tablet_plate_bearing_surface = coordinate_converter.body("tablet_plate_bearing_surface")
    # 4.2 获取打药孔面的z坐标
    strike_drug_parts_center_z = strike_drug_parts_center[2]
    print(tablet_plate_bearing_surface, strike_drug_parts_center_z)
    # 4.3 移动z轴对齐，稍微高1mm
    go.only_z(tablet_plate_bearing_surface, (strike_drug_parts_center_z + 1), 2000)

    # 5、y轴推出让药片最前端对准打药孔中心
    # 5.1 获取当前药片支撑装置的最前面y坐标，默认此为药片最前端
    the_front_supporting_parts = coordinate_converter.body("the_front_supporting_parts")
    # 5.2 获取打药孔中心的y坐标
    strike_drug_parts_center_y = strike_drug_parts_center[1]
    print(the_front_supporting_parts, strike_drug_parts_center_y)
    # 5.3 移动y轴对准位置
    go.only_y(the_front_supporting_parts, strike_drug_parts_center_y, 1000)

    # 6、至此打药前的准备完成，到达指定位置，返回函数
    return


# 初始化设定
def setup():
    return True


# 循环部分
def loop():
    strike_drug_ready()


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
