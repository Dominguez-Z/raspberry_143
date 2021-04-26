#!/usr/bin/env python 
# -*- coding:utf-8 -*-
##########################################################################################################
#   File name:  constant_coordinates.py
#      Author:  钟东佐
#       Date        ||      describe
#   2020/5/19       ||  负责constant_coordinates.json 文件信息获取和管理
#   2021/3/16       ||  整理constant_coordinates.json 文件中的数据：
#                       保留固定的坐标信息，移除会运动的 body 元素，交给coordinate_converter处理
##########################################################################################################
"""
该模块主要用于获取constant_coordinates.json 文件中的数据
constant_coordinates.json 文件中的数据说明如下：

Parameters
----------
motor
    waiting_point
    ready_check_point
    begin_check
strike_drug_parts
    1
    center
    the_top
    the_back
    2
    center
    the_top
    the_back
    3
    center
    the_top
    the_back
plate
    ready_point

Returns
-------

Raises
------

"""

import json
import os
# ############################ 常数值设定区域 ############################
current_path = os.path.dirname(__file__)        # 获取本文件的路径
constant_coordinates_file_path = current_path + "/data/constant_coordinates.json"     # 加上目标文件的相对路径
# ########################################################################


# ############################### 函数说明 ###############################
# 读取constant_coordinates.json文件获取key指的坐标并返回
# ########################################################################
def get(key1=None, key2=None, key3=None):
    """
    获取constant_coordinates.json 文件中的数据
    constant_coordinates.json 文件中的数据说明如下：
    Parameters
    ----------
    motor
        waiting_point
        ready_check_point
        begin_check
    strike_drug_parts
        1
        center
        the_top
        the_back
        2
        center
        the_top
        the_back
        3
        center
        the_top
        the_back
    plate
        ready_point

    Returns
    -------

    Raises
    ------

    """
    f = open(constant_coordinates_file_path)                            # 打开位置坐标文件
    constant_coordinates_all = json.load(f)                             # 加载文件中所用内容
    f.close()                                                           # 关闭文件
    # print(constant_coordinates_all)
    if key3:
        constant_coordinates_key_value = constant_coordinates_all[key1][key2][key3]     # 根据指定的键值key获取数值value
    elif key2:
        constant_coordinates_key_value = constant_coordinates_all[key1][key2]           # 根据指定的键值key获取数值value
    else:
        constant_coordinates_key_value = constant_coordinates_all[key1]                 # 根据指定的键值key获取数值value
    # print("成功获取坐标%s" % constant_coordinates_key_value)            # 打印获取的数值
    return constant_coordinates_key_value                               # 返回获取的数值


# 初始化设定
def setup():
    return True


# 循环部分
def loop():
    print(get('motor' , "ready_check_point"))
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
