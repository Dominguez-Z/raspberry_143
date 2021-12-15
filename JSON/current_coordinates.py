#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  current_coordinates.py
#      Author:  钟东佐
#       Date        ||      describe
#   2020/5/13       ||  以json文件的方式获取和记录各轴坐标信息
#########################################################
import json
import os
# ############################ 常数值设定区域 ############################
current_path = os.path.dirname(__file__)        # 获取本文件的路径
current_coordinates_file_path = current_path + "/data/current_coordinates.json"     # 加上目标文件的相对路径
# ########################################################################


def get(key):
    """
    读取current_coordinates.json文件获取key指的坐标

    Parameters
    ----------
    key
        指定需要的是哪条轴：
        "motor_y1",
        "motor_x1",
        "motor_x",
        "motor_y",
        "motor_z"

    Returns
    -------
    return
        current_coordinates - 指定轴的坐标
    """
    f = open(current_coordinates_file_path)                     # 打开位置坐标文件
    current_coordinates_all = json.load(f)                      # 加载文件中所用内容
    f.close()                                                   # 关闭文件
    current_coordinates = current_coordinates_all[key]          # 根据指定的键值key获取数值value
    # print("成功获取坐标%s" % current_coordinates_xyz)           # 打印获取的数值
    return current_coordinates                                  # 返回获取的数值


# ############################### 函数说明 ###############################
# 更新current_coordinates.json文件中key指定的坐标
# ########################################################################
def record(key, value):
    f = open(current_coordinates_file_path)                     # 打开位置坐标文件
    current_coordinates_all = json.load(f)                      # 加载文件中所用内容
    f.close()                                                   # 关闭文件
    # print("原有坐标%s" % current_coordinates[key])              # 打印原有key指定的数值
    current_coordinates_all[key] = value                        # 修改key指定的数值为接收到的value
    # print("更新后坐标%s" % current_coordinates[key])            # 打印修改后key指定的数值
    # 注意json文件中有中文内容，需要注明编码格式encoding及ensure_ascii
    f = open(current_coordinates_file_path, 'w', encoding='utf-8')          # 打开位置坐标文件并指定为可写
    json.dump(current_coordinates_all, f, ensure_ascii=False, indent=4)     # 写入修改好后的全部坐标
    f.close()                                                   # 关闭文件


# 初始化设定
def setup():
    return True


# 循环部分
def main():
    print(get('motor_x1'))
    # record('body_xyz', [3, 6, 1])
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
        main()
    except KeyboardInterrupt:  # 当按下 'Ctrl+C', 子函数 destroy()将会运行，用于停止退出
        print("程序已停止退出...")
        destroy()
