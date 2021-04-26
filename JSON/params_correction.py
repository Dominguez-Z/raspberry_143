#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################################
#   File name:  params_correction.py
#      Author:  钟东佐
#       Date        ||      describe
#   2021/3/23       ||  params_correction.json 文件信息获取和管理
#                       该文件保存的是参数修正的资料，例如影像识别出误差后，保存到该文件内
#                       电机控制时获取相关数值作为误差修正添加到计算中
#########################################################################
import json
import os
import collections
# ############################ 常数值设定区域 ############################
current_path = os.path.dirname(__file__)        # 获取本文件的路径
params_correction_file_path = current_path + "/data/params_correction.json"     # 加上目标文件的相对路径
# ########################################################################


# ############################### 函数说明 ###############################
# 获取文件中记录的所有位置坐标并放回
# ########################################################################
def get_all():
    f = open(params_correction_file_path)                         # 打开记录柜桶坐标的json文件
    # 加载文件中所用内容
    # object_pairs_hook=collections.OrderedDict用于保证读取回来的数据按照原有键值的顺序
    params_correction_all = json.load(f, object_pairs_hook=collections.OrderedDict)
    f.close()                                               # 关闭文件
    return params_correction_all                                  # 返回获取的数值


def get_ark_barrels(row, line):
    """
    获取指定柜桶的在位置初始化对准过程中的修正参数，数据[x, y, z]
    包含正负，使用过程用加法，加在目标坐标中。

    Parameters
    ----------
    row
        需要修改参数柜桶所在的行，0开始
    line
        需要修改参数柜桶所在的列，0开始
        例如：4行5列，key = "3-4"

    Returns
    -------
    return
        ark_barrel_xyz - [x, y, z]
        "x" : x轴方向上的参数修正
        "y" : y轴方向上的参数修正
        "z" : z轴方向上的参数修正
    """
    f = open(params_correction_file_path)                                   # 打开位置坐标文件
    ark_barrels_coordinates_all = json.load(f)                              # 加载文件中所用内容
    f.close()                                                               # 关闭文件
    key = str(str(row) + "-" + str(line))  # 整合出键值
    correction_xyz = ark_barrels_coordinates_all["ark_barrels"][key]       # 根据指定的键值key获取数值value
    # print("成功获取坐标%s" % current_coordinates_xyz)                   # 打印获取的数值
    return correction_xyz


# ############################### 函数说明 ###############################
# 更新current_coordinates.json文件中key指定的坐标
# ########################################################################
def record_ark_barrels(row, line, deviation: list):
    """
    用于更新柜桶坐标的误差，在原有的记录中 + 目前的输入值

    Parameters
    ----------
    row
        需要修改参数柜桶所在的行，0开始
    line
        需要修改参数柜桶所在的列，0开始
    deviation
        [x, y, z],格式规定为列表，依次是对应坐标的修改量。
        修正量的正负号规定：控制轴根据输入 关注点当前坐标和目标坐标运动 后，
        由于机械等误差原因造成，关注点并非在目标出，
        修改量 = 目标坐标 - 当前坐标。得出修改量
    """
    # 获取整个文件的信息
    params_correction_all = get_all()
    # 获取指定柜桶原有的修正值
    key = str(str(row) + "-" + str(line))       # 整合出键值
    old_param = params_correction_all["ark_barrels"][key]
    # 判断输入的修改量列表与记录的一直
    if len(old_param) == len(deviation):
        new_param = [old_param[i] + deviation[i] for i in range(len(old_param))]
        params_correction_all["ark_barrels"][key] = new_param         # 修改key指定的数值为接收到的value
        # print("更新后坐标%s" % current_coordinates[key])            # 打印修改后key指定的数值
        f = open(params_correction_file_path, 'w')                # 打开位置坐标文件并指定为可写
        json.dump(params_correction_all, f, indent=2)             # 写入修改好后的全部坐标
        f.close()                                                   # 关闭文件
        print("修正参数更新成功")
        return
    else:
        print("修正参数更新失败")
        return


# 初始化设定
def setup():
    return True


# 循环部分
def loop():
    record_ark_barrels(0, 0, [1, -1, 0])


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
