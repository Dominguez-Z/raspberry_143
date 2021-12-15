#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################################
#   File name:  ark_barrels_coordinates.py
#      Author:  钟东佐
#       Date        ||      describe
#   2020/5/13       ||  ark_barrels_coordinates.json 文件信息获取和管理
#########################################################################
import json
import os
import collections
import numpy as np
# ############################ 常数值设定区域 ############################
current_path = os.path.dirname(__file__)        # 获取本文件的路径
ark_barrels_file_path = current_path + "/data/ark_barrels_coordinates.json"     # 加上目标文件的相对路径
# ########################################################################


# ############################### 函数说明 ###############################
# 获取文件中记录的所有位置坐标并放回
# ########################################################################
def get_all():
    f = open(ark_barrels_file_path)                         # 打开记录柜桶坐标的json文件
    # 加载文件中所用内容
    # object_pairs_hook=collections.OrderedDict用于保证读取回来的数据按照原有键值的顺序
    ark_barrels_coordinates_all = json.load(f, object_pairs_hook=collections.OrderedDict)
    f.close()                                               # 关闭文件
    # 只获取柜桶坐标
    ark_barrels_all = ark_barrels_coordinates_all["ark_barrels"]
    return ark_barrels_all                                  # 返回获取的数值


def get_bottle(row, line):
    """
    获取指定药瓶柜桶的坐标数据[x, y, z]

    Parameters
    ----------
    row
        柜桶所在的行，0开始
    line
        柜桶所在的列，0开始
        例如：4行5列，key = "3-4"

    Returns
    -------
    return
        ark_barrel_xyz - [x, y, z]
        "x" : 转动装置传动位x方向中心线
        "y" : 转动装置y方向最小坐标，既推杆刚好接触传动装置
        "z" : 转动装置呈水平状态时，与推杆上表面的接触面坐标
    """
    # =========== 旧的获取方式 ===========
    # f = open(ark_barrels_file_path)                             # 打开位置坐标文件
    # ark_barrels_coordinates_all = json.load(f)                              # 加载文件中所用内容
    # f.close()                                                   # 关闭文件
    # key = str(str(row) + "-" + str(line))  # 整合出键值
    # ark_barrel_xyz = ark_barrels_coordinates_all["bottle"][key]       # 根据指定的键值key获取数值value
    # # print("成功获取坐标%s" % current_coordinates_xyz)           # 打印获取的数值

    # 获取指定柜桶的柜桶数据
    ark_barrel_xyz = get(row, line)

    # 获取摇药装置的偏移数据
    f = open(ark_barrels_file_path)                                     # 打开位置坐标文件
    ark_barrels_coordinates_all = json.load(f)                          # 加载文件中所用内容
    f.close()
    bottle_offset_xyz = ark_barrels_coordinates_all["bottle"]["offset"]
    bottle_xyz = np.array(ark_barrel_xyz) + np.array(bottle_offset_xyz)

    return bottle_xyz                                                   # 返回获取的数值


def get_plate(row, line):
    """
    获取指定药板柜桶的坐标数据[x, y, z]

    Parameters
    ----------
    row
        柜桶所在的行，0开始
    line
        柜桶所在的列，0开始
        例如：4行5列，key = "3-4"

    Returns
    -------
    return
        ark_barrel_xyz - [x, y, z]
        "x" : 柜桶x轴方向上的中心线坐标
        "y" : 所有柜桶前面板外表面的坐标
        "z" : 前面板柜桶镂空处支撑柜桶的接触面的坐标
    """
    f = open(ark_barrels_file_path)                             # 打开位置坐标文件
    ark_barrels_coordinates_all = json.load(f)                              # 加载文件中所用内容
    f.close()                                                   # 关闭文件
    key = str(str(row) + "-" + str(line))  # 整合出键值
    ark_barrel_xyz = ark_barrels_coordinates_all["plate"][key]       # 根据指定的键值key获取数值value
    # print("成功获取坐标%s" % current_coordinates_xyz)           # 打印获取的数值
    return ark_barrel_xyz                                           # 返回获取的数值


def get_plate_y(key=None):
    """
    获取和柜桶y方向的数据，该数据对于所有柜桶是统一的：

    Parameters
    ----------
    key
        json文件中["plate"]y标签下的数据：
        "image_recognition"：柜桶影像识别的两条竖线到前面板外表面的位移，含正负

    Returns
    -------
    return
        key_value - 指定键的值

    """
    f = open(ark_barrels_file_path)             # 打开位置坐标文件
    ark_barrels_coordinates_all = json.load(f)  # 加载文件中所用内容
    f.close()                                   # 关闭文件
    if key:
        key_value = ark_barrels_coordinates_all["plate"]["y"][key]          # 根据指定的键值key获取数值value
    else:
        # 没有指定将"y"包含的全部一起返回
        key_value = ark_barrels_coordinates_all["plate"]["y"]
    # print("成功获取坐标%s" % current_coordinates_xyz)           # 打印获取的数值
    return key_value


def get_plate_z(key=None):
    """
    获取和柜桶z方向的数据，该数据对于所有柜桶是统一的：

    Parameters
    ----------
    key
        json文件中["plate"]z标签下的数据：
        "hog_back"：药片存放前端防止药片掉出的拱起 相对于 药片板支撑面的 高度，恒为正
        "baseboard"：药片板支撑面的 相对于 前面板柜桶镂空处支撑柜桶的接触面 的高度，恒为正

    Returns
    -------
    return
        key_value - 指定键的值

    """
    f = open(ark_barrels_file_path)             # 打开位置坐标文件
    ark_barrels_coordinates_all = json.load(f)  # 加载文件中所用内容
    f.close()                                   # 关闭文件
    if key:
        key_value = ark_barrels_coordinates_all["plate"]["z"][key]          # 根据指定的键值key获取数值value
    else:
        # 没有指定将"z"包含的全部一起返回
        key_value = ark_barrels_coordinates_all["plate"]["z"]
    # print("成功获取坐标%s" % current_coordinates_xyz)           # 打印获取的数值
    return key_value


def get(row, line):
    """
    获取指定柜桶的坐标数据[x, y, z],

    Parameters
    ----------
    row
        柜桶所在的行，0开始
    line
        柜桶所在的列，0开始
        例如：4行5列，key = "3-4"

    Returns
    -------
    return
        ark_barrel_xyz - [x, y, z]
        "x" : 柜桶x轴方向上的中心线坐标
        "y" : 所有柜桶前面板外表面的坐标
        "z" : 前面板柜桶镂空处支撑柜桶的接触面的坐标
    """
    f = open(ark_barrels_file_path)             # 打开位置坐标文件
    all_info = json.load(f)                     # 加载文件中所用内容
    f.close()                                   # 关闭文件
    origin_xyz = all_info["arks"]["0-0"]        # 0-0柜桶的坐标值
    x_distance = all_info["arks"]["x_distance"]     # 相邻列的位置差
    z_distance = all_info["arks"]["z_distance"]     # 相邻行的高度差
    # 计算指定柜桶的坐标数据，计算结果保留两位
    ark_barrel_xyz = []
    specify_x = round(origin_xyz[0] + x_distance * line, 2)   # 列
    specify_z = round(origin_xyz[2] + z_distance * row , 2)   # 行
    # 依次添加进数列,
    ark_barrel_xyz.append(specify_x)
    ark_barrel_xyz.append(origin_xyz[1])
    ark_barrel_xyz.append(specify_z)

    # print("成功获取坐标%s" % ark_barrel_xyz)           # 打印获取的数值
    return ark_barrel_xyz                                           # 返回获取的数值


def get_y(key=None):
    """
    获取和柜桶y方向的数据，该数据对于所有柜桶是统一的：

    Parameters
    ----------
    key
        json文件中["arks"]y标签下的数据：
        "image_recognition"：柜桶影像识别的两条竖线到前面板外表面的位移，含正负

    Returns
    -------
    return
        key_value - 指定键的值

    """
    f = open(ark_barrels_file_path)             # 打开位置坐标文件
    ark_barrels_coordinates_all = json.load(f)  # 加载文件中所用内容
    f.close()                                   # 关闭文件
    if key:
        key_value = ark_barrels_coordinates_all["arks"]["y"][key]          # 根据指定的键值key获取数值value
    else:
        # 没有指定将"y"包含的全部一起返回
        key_value = ark_barrels_coordinates_all["arks"]["y"]
    # print("成功获取坐标%s" % current_coordinates_xyz)           # 打印获取的数值
    return key_value


def get_z(key=None):
    """
    获取和柜桶z方向的数据，该数据对于所有柜桶是统一的：

    Parameters
    ----------
    key
        json文件中["arks"]z标签下的数据：
        "hog_back"：药片存放前端防止药片掉出的拱起 相对于 药片板支撑面的 高度，恒为正
        "baseboard"：药片板支撑面的 相对于 前面板柜桶镂空处支撑柜桶的接触面 的高度，恒为正
        "qr_code"：标准柜桶二维码z中线 相对于 前面板柜桶镂空处支撑柜桶的接触面 高度，恒为正

    Returns
    -------
    return
        key_value - 指定键的值

    """
    f = open(ark_barrels_file_path)             # 打开位置坐标文件
    ark_barrels_coordinates_all = json.load(f)  # 加载文件中所用内容
    f.close()                                   # 关闭文件
    if key:
        key_value = ark_barrels_coordinates_all["arks"]["z"][key]          # 根据指定的键值key获取数值value
    else:
        # 没有指定将"z"包含的全部一起返回
        key_value = ark_barrels_coordinates_all["arks"]["z"]
    # print("成功获取坐标%s" % current_coordinates_xyz)           # 打印获取的数值
    return key_value


# 初始化设定
def setup():
    return True


# 循环部分
def loop():
    print(get(0, 7))
    print(get_bottle(0, 7))
    print([1, 2, 4])


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
