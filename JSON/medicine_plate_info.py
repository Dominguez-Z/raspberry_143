#!/usr/bin/env python 
# -*- coding:utf-8 -*-
"""
管理mediacine_plate目录下的所有药板信息的json文件
"""
#########################################################
#   File name:  medicine_plate_info.py
#      Author:  钟东佐
#       Date        ||      describe
#   2021/9/30       ||  创建读取药板信息函数
#########################################################
import json
import os
# ############################ 常数值设定区域 ############################
current_path = os.path.dirname(__file__)        # 获取本文件的路径
current_file_path = current_path + "/medicine_plate/"     # 加上目标目录的相对路径
# ########################################################################


def get(medicine_num):
    """
    药板信息获取，根据输入的药板编号获取对应药板的所有信息

    Parameters
    ----------
    medicine_num
        药物的编号，具有唯一性

    Returns
    -------
    return
        plate_info - 该药板编号json文件的所有信息
    """

    plate_info_file_path = current_path + "/../JSON/medicine_plate/" + str(medicine_num) + ".json"
    f = open(plate_info_file_path)                              # 打开药板文件
    plate_info_all = json.load(f)                               # 加载文件中所用内容
    f.close()                                                   # 关闭文件
    return plate_info_all


def setup():
    """
    初始化设定

    """
    return True


def main():
    """
    主函数

    """
    # print(get('motor_x1'))
    # record('body_xyz', [3, 6, 1])
    print(get_info(6924168200093))
    return


def destroy():
    """
    结束释放

    """
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
