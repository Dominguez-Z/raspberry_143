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
    f = open(ark_barrels_file_path)                             # 打开位置坐标文件
    ark_barrels_coordinates_all = json.load(f)                              # 加载文件中所用内容
    f.close()                                                   # 关闭文件
    key = str(str(row) + "-" + str(line))  # 整合出键值
    ark_barrel_xyz = ark_barrels_coordinates_all["bottle"][key]       # 根据指定的键值key获取数值value
    # print("成功获取坐标%s" % current_coordinates_xyz)           # 打印获取的数值
    return ark_barrel_xyz                                           # 返回获取的数值


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


def get_plate_y(key):
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
    key_value = ark_barrels_coordinates_all["plate"]["y"][key]          # 根据指定的键值key获取数值value
    # print("成功获取坐标%s" % current_coordinates_xyz)           # 打印获取的数值
    return key_value


def get_plate_z(key):
    """
    获取和柜桶z方向的数据，该数据对于所有柜桶是统一的：

    Parameters
    ----------
    key
        json文件中["plate"]y标签下的数据：
        "hog_back"：药片存放前端防止药片掉出的拱起 相对于 药片板支撑面的 高度，不包含正负

    Returns
    -------
    return
        key_value - 指定键的值

    """
    f = open(ark_barrels_file_path)             # 打开位置坐标文件
    ark_barrels_coordinates_all = json.load(f)  # 加载文件中所用内容
    f.close()                                   # 关闭文件
    key_value = ark_barrels_coordinates_all["plate"]["z"][key]          # 根据指定的键值key获取数值value
    # print("成功获取坐标%s" % current_coordinates_xyz)           # 打印获取的数值
    return key_value


# 初始化设定
def setup():
    return True


# 循环部分
def loop():
    ark_barrels = get_all()
    print(ark_barrels)


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
