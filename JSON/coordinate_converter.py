#!/usr/bin/env python 
# -*- coding:utf-8 -*-
##########################################################################################################
#   File name:  coordinate_converter.py
#      Author:  钟东佐
#       Date        ||      describe
#   2020/5/25       ||  坐标转换器，将JSON文件记录的电机坐标motor_x,_y,_z等转换成
#                       关注点的坐标，用于作为当前目标输入到go模块中的相应函数，方便计算需要行走的位移量。
#   2021/3/16       ||  依据：coordinate_converter.json 文件记录的仅仅是用于计算当前目标需要的机械数据
#                       修正原本需要从constant_coordinates获取的数据，添加自己的get函数
##########################################################################################################
import JSON.current_coordinates as current_coordinates
import json
import os
# ############################ 常数值设定区域 ############################
current_path = os.path.dirname(__file__)        # 获取本文件的路径
current_coordinates_file_path = current_path + "/data/coordinates_converter.json"     # 加上目标文件的相对路径
# ########################################################################


# ############################### 函数说明 ###############################
# 读取coordinates_converter.json文件获取key指的坐标并返回
# ########################################################################
def get(key1=None, key2=None, key3=None):
    f = open(current_coordinates_file_path)                            # 打开位置坐标文件
    current_coordinates_all = json.load(f)                             # 加载文件中所用内容
    f.close()                                                           # 关闭文件
    # print(current_coordinates)
    # 根据指定的键值key获取数值value
    if key3:
        constant_coordinates_key_value = current_coordinates_all[key1][key2][key3]     
    elif key2:
        constant_coordinates_key_value = current_coordinates_all[key1][key2]           
    else:
        constant_coordinates_key_value = current_coordinates_all[key1]                 
    # print("成功获取坐标%s" % constant_coordinates_key_value)            # 打印获取的数值
    return constant_coordinates_key_value                               # 返回获取的数值


def body_cusp_center():
    """
    将motor坐标转化为 主体尖端中心 的空间坐标[x, y, z]

    Returns
    -------
    return
        current_coordinates_body_cusp_center - [x, y, z]
        "x" : 两个夹具的中心线坐标
        "y" : 顶起药片板尖端的最前端
        "z" : 顶起药片板尖端的下表面
    """
    # 获取当前各轴的轴坐标
    current_coordinates_motor = list()
    current_coordinates_motor.append(current_coordinates.get('motor_x'))
    current_coordinates_motor.append(current_coordinates.get('motor_y'))
    current_coordinates_motor.append(current_coordinates.get('motor_z'))
    # 获取主体尖端的修正数据
    cusp_center = get("body", "cusp_center")
    # 电机轴坐标 + 尖端的修正数据 = 整机坐标系的尖端坐标
    if len(current_coordinates_motor) == len(cusp_center):
        current_coordinates_body_cusp_center = []
        for i in range(len(cusp_center)):
            current_coordinates_body_cusp_center_1 = current_coordinates_motor[i] + cusp_center[i]
            current_coordinates_body_cusp_center.append(current_coordinates_body_cusp_center_1)
    else:
        print("坐标长度不对，请检查")
        return
    # print(current_coordinates_motor)
    # print(cusp_center)
    # print(current_coordinates_body_cusp_center)
    return current_coordinates_body_cusp_center


def body_push_rod(key):
    """
        将motor坐标转化为 主体推杆 的指定位置坐标

        Parameters
        ----------
        key
            推杆上需要获取的关注点：
            "center"：推杆x方向的中心线
            "the_top"：推杆弯钩z方向上表面
            "the_bottom"：推杆直杆z方向下表面
            "the_front"：推杆y方向前表面

        Returns
        -------
        return
            current_coordinates_key - 指定部位当前的空间坐标
        """
    # 0、创建一个查询目标轴的字典
    push_rod = {
        "center": 'motor_x',
        "the_top": 'motor_z',
        "the_bottom": 'motor_z',
        "the_front": 'motor_y'
    }

    # 1、获取指定位置的零点位坐标
    coordinates_key = get("body", "push_rod", key)
    print(coordinates_key)

    # 2、根据指定位置获取需要得知轴的目前坐标
    # 2.1 查字典获取目标轴
    motor_key = push_rod.get(key)
    # 2.2 获取目标轴坐标
    current_coordinates_motor = current_coordinates.get(motor_key)

    # 3、计算指定部位的空间坐标
    current_coordinates_key = current_coordinates_motor + coordinates_key

    # 4、完成转换，返回目标值
    return current_coordinates_key


def body_tong(key):
    """
    将motor坐标转化为 夹具上 的指定位置坐标

    Parameters
    ----------
    key
        夹药装置上需要获取的关注点：
        "open_center"：夹具张开最大时，z方向的中心，用于夹药时药片板进入。
        "open_top"：夹具张开口z方向的顶部，用于定位药板拉出时候的高度。
        "the_front_y"：夹具y方向最前端，用于控制夹取药板边缘的厚度。

    Returns
    -------
    return
        current_coordinates_key - 指定部位当前的空间坐标
    """
    # 0、创建一个查询目标轴的字典
    # 'motor_y_y1',说明该位置受到y和y1轴同时影响
    tong = {
        "open_center": 'motor_z',
        "open_top": 'motor_z',
        "the_front_y": 'motor_y_y1'
    }

    # 1、获取指定位置的零点位坐标
    coordinates_key = get("body", "tong", key)
    print(coordinates_key)

    # 2、根据指定位置获取需要得知轴的目前坐标
    # 2.1 查字典获取目标轴
    motor_key = tong.get(key)
    # 2.2 获取目标轴坐标
    if motor_key != 'motor_y_y1':
        current_coordinates_motor = current_coordinates.get(motor_key)
    else:
        current_coordinates_motor = current_coordinates.get('motor_y') + \
                                    current_coordinates.get('motor_y1')

    # 3、计算指定部位的空间坐标
    current_coordinates_key = current_coordinates_motor + coordinates_key

    # 4、完成转换，返回目标值
    return current_coordinates_key


def body_drop_channel():
    """
    将motor坐标转化为 主体药物掉落通道口 的空间坐标[x, y, z]

    Returns
    -------
    return
        current_coordinates_body_drop_channel - [x, y, z]
        "x" : 出药口的中心线坐标
        "y" : 出药斜台y方向前边沿
        "z" : 出药斜台往下斜约30度时，前边沿的z高度
    """
    # 获取当前各轴的轴坐标
    current_coordinates_motor = list()
    current_coordinates_motor.append(current_coordinates.get('motor_x'))
    current_coordinates_motor.append(current_coordinates.get('motor_y'))
    current_coordinates_motor.append(current_coordinates.get('motor_z'))
    # 获取主体出药口的修正数据
    drop_channel = get("body", "drop_channel")
    # 电机轴坐标 + 出药口的修正数据 = 整机坐标系的出药口坐标
    if len(current_coordinates_motor) == len(drop_channel):
        current_coordinates_body_drop_channel = []
        for i in range(len(drop_channel)):
            current_coordinates_body_drop_channel_1 = current_coordinates_motor[i] + drop_channel[i]
            current_coordinates_body_drop_channel.append(current_coordinates_body_drop_channel_1)
    else:
        print("坐标长度不对，请检查")
        return
    return current_coordinates_body_drop_channel


def camera(num=None):
    """
    将motor坐标转化为 对应摄像头 的空间坐标[x, y, z]

    Parameters
    ----------
    num
        摄像头编号，1：正对下，照药板和药瓶嘴；2：正对前，照柜桶。

    Returns
    -------
    return
        body_camera - [x, y, z]，摄像头孔的空间坐标，辅助对准拍照部位
    """
    # 如果没有指定摄像头返回失败
    if not num:
        print("未指定摄像头编号，无法获取当前坐标")
        return False

    # 获取当前各轴的轴坐标
    current_coordinates_motor = list()
    current_coordinates_motor.append(current_coordinates.get('motor_x'))
    current_coordinates_motor.append(current_coordinates.get('motor_y'))
    current_coordinates_motor.append(current_coordinates.get('motor_z'))
    # 获取主体出药口的修正数据
    camera_num = get("body", "camera", str(num))
    # 电机轴坐标 + 出药口的修正数据 = 整机坐标系的出药口坐标
    if len(current_coordinates_motor) == len(camera_num):
        current_coordinates_camera = []
        for i in range(len(camera_num)):
            current_coordinates_camera_1 = current_coordinates_motor[i] + camera_num[i]
            current_coordinates_camera.append(current_coordinates_camera_1)
    else:
        print("坐标长度不对，请检查")
        return
    return current_coordinates_camera


def body(key):
    """
    将motor坐标转化为 主体 的指定位置坐标

    Parameters
    ----------
    key
        指定的键。包括：
        "tablet_plate_bearing_surface"：药板拉回后支撑面的上表面
        "the_front_supporting_parts"：药板支撑结构y方向的前表面

    Returns
    -------
    return
        current_coordinates_key - 指定键的值
    """
    # 0、创建一个查询目标轴的字典
    push_rod = {
        "tablet_plate_bearing_surface": 'motor_z',
        "the_front_supporting_parts": 'motor_y',
    }

    # 1、获取指定位置的零点位坐标
    coordinates_key = get("body", key)
    print(coordinates_key)

    # 2、根据指定位置获取需要得知轴的目前坐标
    # 2.1 查字典获取目标轴
    motor_key = push_rod.get(key)
    # 2.2 获取目标轴坐标
    current_coordinates_motor = current_coordinates.get(motor_key)

    # 3、计算指定部位的空间坐标
    current_coordinates_key = current_coordinates_motor + coordinates_key

    # 4、完成转换，返回目标值
    return current_coordinates_key


# 初始化设定
def setup():
    return True


# 循环部分
def main():
    print(camera(2))


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
