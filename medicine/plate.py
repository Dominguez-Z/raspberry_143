#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  plate.py
#      Author:  钟东佐
#       Date        ||      describe
#   2021/03/17      ||  编写从药柜中拿药的代码
#   2021/05/04      ||  编写了放回药板的代码，增加了丢弃药板的代码。
#   2021/06/07      ||  修改打药，实现打多粒药
#########################################################
"""
该模块主要处理对于药板的拿和放的控制。
拿药板调用函数：do_take ；
放回药板调用函数：do_back;
丢弃药板调用函数：throw_away。
打药：strike_drug

"""

import time
import os
import json
import motor.y_drive as y
import motor.x_drive as x
import motor.z_drive as z
import motor.y1_drive as y1
import motor.x1_drive as x1
import motor.go as go
import JSON.coordinate_converter as coordinate_converter
import JSON.ark_barrels_coordinates as ark_barrels_coordinates
import JSON.current_coordinates as current_coordinates
import JSON.params_correction as params_correction
import JSON.constant_coordinates as constant_coordinates
import electromagnet.strike_drug_drive as strike
import threading

# ############################################## 常数值设定区域 ##############################################
# 本文件的路径
current_path = os.path.dirname(__file__)

# do_take、strike_drug_ready
CLIP_MM = 5                 # 夹取药片边缘的宽度
Y_Y1_MM = 7                 # y_y1相对运动夹稳药片板的运动距离
# ############################################################################################################


def y_y1(coordinate_now_y, coordinate_target_y,
         coordinate_now_y1, coordinate_target_y1,
         rpm_max_y=None, rpm_max_y1=None):
    """
    y轴和y1轴同步运动实现夹取点保持不动，上下夹片收紧夹稳药片板
    初步测试，pulse_width_y = 3360，pulse_width_y1 = 1000，近似能同时启动和停止
    最新控制给的是rpm_max，根据各轴的MM_REV，同一速度为120mm/min,那么y给4，y1给30
    
    Parameters
    ----------
    coordinate_now_y
        当前y坐标
    coordinate_target_y
        目标y坐标
    coordinate_now_y1
        当前y1坐标
    coordinate_target_y1
        目标y1坐标
    rpm_max_y
        y轴运动最高转速设定，未指定按照默认
    rpm_max_y1
        y1轴运动最高转速设定，未指定按照默认
    """
    # 创建y、y1轴子线程
    threads = []
    t1 = threading.Thread(target=go.only_y, args=(coordinate_now_y, coordinate_target_y, rpm_max_y,))
    threads.append(t1)
    t2 = threading.Thread(target=go.only_y1, args=(coordinate_now_y1, coordinate_target_y1, rpm_max_y1,))
    threads.append(t2)
    # 将所有子线程开始
    for t in threads:
        t.setDaemon(True)
        t.start()
    # 打开子线程的阻塞保证所有子线程都运行完了，主线程才继续
    for t in threads:
        t.join()
        # print("threads : %s.time is: %s" % (t, ctime()))
    print('go_y_y1_success')
    return 


def get_plate_info(medicine_num):
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

    Raises
    ------
    有东西
    """
    # import collections
    
    # 路径整合
    """
    current_path
        本文件的路径
    constant_coordinates_file_path
        加上目标文件信息后的绝对路径
    """

    plate_info_file_path = current_path + "/../JSON/medicine_plate/" + str(medicine_num) + ".json"
    
    # 获取文件信息
    # object_pairs_hook=collections.OrderedDict用于保证读取回来的数据按照原有键值的顺序
    f = open(plate_info_file_path)
    plate_info = json.load(f)
    # plate_info = json.load(f, object_pairs_hook=collections.OrderedDict)
    f.close()
    
    return plate_info


def x_correct_coordinates(row, line, ark_barrels_x, correction, num_center: int):
    """
    计算获取完成 将body上的夹子中心修正，使之对齐目标药板的中心 任务的坐标

    Parameters
    ----------
    row
        目前所在柜桶的行
    line
        目前所在柜桶的列
    ark_barrels_x
        柜桶x方向上的信息。
        "num_center"：药的列数，有些药窄的一个柜桶可能有两列。
        "center_deviation"：药列的中心相对于柜桶中心的偏移量，因为两列时是轴对称，顾只需记录一个值
    correction
        坐标修正，含正负，加法使用
    num_center
        目标药板位于该柜桶的第几列，顺x轴正方向增加,0 or 1

    Returns
    -------
    return
        body_cusp_center_x - 当前主体尖端的x坐标，
        ark_barrels_x_center - 目标柜桶x轴中心线坐标
    """

    # 获取目标柜桶的坐标
    target_coordinates_x = ark_barrels_coordinates.get_plate(row, line)[0]
    # 获取当前主体的坐标
    body_cusp_center_x = coordinate_converter.body_cusp_center()[0]
    # 目标位置 = 目标柜桶x坐标 +/- 中心偏移量 + 修正量
    if 0 <= num_center < ark_barrels_x["num_center"]:        # 保证指定柜桶在记录的范围内
        if num_center == 0:
            ark_barrels_x_center = target_coordinates_x - ark_barrels_x["center_deviation"] + correction
        else:
            ark_barrels_x_center = target_coordinates_x + ark_barrels_x["center_deviation"] + correction
        # # x轴运动
        # go.only_x(body_cusp_center_x, target_x)
        print("134：完成修正x对准药板的参数运算")
    else:
        # x轴参数不对，x轴不动
        ark_barrels_x_center = body_cusp_center_x
        print("136：指定的 ’num_center’ 参数不在[0, %s)" % ark_barrels_x["num_center"])
        print("没有修正x对准药板，位移为0")
    return body_cusp_center_x, ark_barrels_x_center


def z_correct_coordinates(row, line, ark_barrels_z_dis, correction):
    """
    计算获取完成 z轴对齐，使得顶起药板的尖端下表面与药柜中支撑药板的面平齐 任务的坐标

    Parameters
    ----------
    row
        目前所在柜桶的行
    line
        目前所在柜桶的列
    ark_barrels_z_dis
        柜桶z方向上的信息。
        "baseboard"：支撑药片板铁片的上表面z坐标。
    correction
        坐标修正，含正负，加法使用
        
    Returns
    -------
    return
        body_cusp_center_z - 当前主体尖端的z坐标，
        z_baseboard - 当前柜桶支撑药板底表面坐标，用于后续z方向计算的基础

    Raises
    ------
    后续镜头2需要可能要调整对齐位置
    """
    # 获取目标柜桶的z坐标
    ark_barrels_z = ark_barrels_coordinates.get_plate(row, line)[2]
    # 获取当前主体尖端的z坐标
    body_cusp_center_z = coordinate_converter.body_cusp_center()[2]
    # 目标位置 = 目标柜桶z坐标 + 底板表面相对量 + 修正量
    z_baseboard = ark_barrels_z + ark_barrels_z_dis["baseboard"] + correction
    # # z轴运动
    # go.only_z(body_cusp_center_z, z_baseboard)
    print("168：完成修正z对准药片板支撑铁片的坐标运算")
    return body_cusp_center_z, z_baseboard


def y_correct(correction, reserved_distance=0):
    """
    y轴修正，前进到 尖端 与 影像识别边 相距 指定的 mm

    Parameters
    ----------
    reserved_distance
        尖端 与 影像识别边 预留的距离，默认为0mm
    correction
        坐标修正，含正负，加法使用

    Returns
    -------
    return
        image_recognition_coordinate - 该柜桶影像识别边的y坐标，可作为后续y方向计算基础
    """
    # 获取当前主体尖端的y坐标
    body_cusp_center_y = coordinate_converter.body_cusp_center()[1]
    # 获取目标柜桶的y坐标
    # 目前设计每个柜桶y坐标都是一样的
    # 设定的是前面板外表面坐标，因此用[0, 0]柜桶的代替所有
    ark_barrels_y = ark_barrels_coordinates.get_plate(1, 0)[1]
    image_recognition_distance = ark_barrels_coordinates.get_plate_y("image_recognition")
    # 影像识别边坐标 = 目标柜桶y坐标 + 影像识别边距离  + 修正量
    image_recognition_coordinate = ark_barrels_y + image_recognition_distance + correction
    # 目标位置 = 影像识别边坐标 - 预留距离
    target_y = image_recognition_coordinate - reserved_distance
    # y轴运动
    go.only_y(body_cusp_center_y, target_y)
    print(body_cusp_center_y, target_y)
    print("192：完成修正y,前进到与影像识别边相距%smm" % reserved_distance)
    return image_recognition_coordinate


def x1_correct(width):
    """
    x1轴调整，夹子宽度调整到目标药板宽度
    Parameters
    ----------
    width
        药片板的宽度
    """
    # x1轴运动
    go.only_x1(width)
    print("206：完成修正x1,药夹宽度与药片板一致")
    return


def y1_correct():
    """
    y1轴修正，达到最前端,也就是目前的归零
    """
    # 获取当前y1的坐标
    current_coordinates_y1 = current_coordinates.get("motor_y1")
    # y1运动至0
    go.only_y1(current_coordinates_y1, 0)
    print("218：完成修正y1,到达坐标0，既到达最前端")
    return


def do_take(medicine_num, row, line, num_center=0):
    """
    调用该函数实现拿取药板

    Parameters
    ----------
    medicine_num
        药物的编号，具有唯一性
    row
        目前所在柜桶的行，0开始，顺轴正向增加
    line
        目前所在柜桶的列，0开始，顺轴正向增加
    num_center
        目标药板位于该柜桶的第几列，顺x轴正方向增加,0 or 1，默认是0
    """
    # ############################################## 常数值设定区域 ##############################################
    clip_mm = CLIP_MM     # 夹取药片边缘的宽度
    y_y1_mm = Y_Y1_MM     # y_y1相对运动夹稳药片板的运动距离
    sleep_time = 0.1        # 动作运动间隔的时间
    # ############################################################################################################

    # 1、获取需要的数据
    # 1.1 指定药物编号的json数据
    plate_info = get_plate_info(medicine_num)
    # 1.2 指定药柜的修正参数
    params_correction_xyz = params_correction.get_ark_barrels(row, line)
    # 1.3 柜桶相关信息
    ark_z_info = ark_barrels_coordinates.get_plate_z()

    # 2、五轴修正
    # 2.0 xz平面运动前提是y方向不会碰撞
    go.xz_move_y_safe()
    time.sleep(sleep_time)
    # 2.1 x1轴修正，夹子宽度调整到目标药板宽度
    x1_correct(plate_info["width"])
    time.sleep(sleep_time)
    # 2.2 y1轴修正，达到最前端
    y1_correct()
    time.sleep(sleep_time)

    # 2.3 x，z轴对准参数获取
    body_cusp_center_x, ark_barrels_x_center = \
        x_correct_coordinates(row, line, plate_info["ark_barrels"]["x"], params_correction_xyz[0], num_center)
    body_cusp_center_z, z_baseboard = \
        z_correct_coordinates(row, line, ark_z_info, params_correction_xyz[2])
    z_base_2_target = z_baseboard + 15.3     # 对准换为影像识别的底边

    # 2.4 x轴修正对齐，夹子中心对齐柜桶中心,z轴修正对齐，尖端底部与药板支撑面平齐
    # 同时进行节约时间
    go.xz(coordinate_now_x=body_cusp_center_x,
          coordinate_target_x=ark_barrels_x_center,
          coordinate_now_z=body_cusp_center_z,
          coordinate_target_z=z_base_2_target)
    time.sleep(sleep_time)

    # # 2.3 x轴修正对齐，夹子中心对齐柜桶中心
    # x_correct(row, line, plate_info["ark_barrels"]["x"], params_correction_xyz[0], 0)
    # time.sleep(sleep_time)
    # # 2.4、z轴修正对齐，尖端底部与药板支撑面平齐
    # z_baseboard = z_correct(row, line, plate_info["ark_barrels"]["z"], params_correction_xyz[2])
    # time.sleep(sleep_time)

    # 2.5 y轴修正，前进到 尖端 与 影像识别边 相距 0mm
    image_recognition_coordinate = y_correct(params_correction_xyz[1], 0)
    # y_correct(params_correction_xyz[1], 0)
    time.sleep(sleep_time)

    # 3、前提是五轴已经对准初始位置，开始取药
    # z轴上升到前端二铁片位于最底药板之上，目前测量距离为  mm
    '''
    修正中z轴对准实现了尖端下表面与药片板下表面平齐，
    z轴向上移动 (药板总厚度 + 底面面厚度)/2 ，
    便能使尖端处于两片药的中间位置
    '''
    # 获取当前主体尖端的z坐标
    body_cusp_center_z = coordinate_converter.body_cusp_center()[2]
    # 最底两块药片缝隙中心 柜桶底表面 + (药板总厚度+药锡纸板厚度)/2
    z_target0 = z_baseboard + (plate_info["agg_thickness"] + plate_info["thickness"])/2
    go.only_z(body_cusp_center_z, z_target0)
    time.sleep(sleep_time)

    # Y轴运动将铁片插入最下药板和上一片药板之间，然后Z轴调整至夹具张口中心与药片板夹取位置相平的位置
    y_move1 = 12
    go.only_y(0, y_move1)
    time.sleep(sleep_time)
    # 获取当前主体夹具开口中心
    body_tong_open_center = coordinate_converter.body_tong("open_center")
    # 最底药板的夹取中心 柜桶底表面 + 药锡纸板厚度/2 + 底下药板被上面影响抬起的高度1mm
    z_target1 = z_baseboard + plate_info["thickness"]/2 + 1
    go.only_z(body_tong_open_center, z_target1)
    time.sleep(sleep_time)

    # Y轴进一步插入，使得药片板位于夹片之间
    # 机械上药片板边缘比影像识别边前 6mm
    # 夹具夹取药板边缘 clip_mm
    # 获取当前主体夹具前表面坐标
    the_front_tong_1 = coordinate_converter.body_tong("the_front_y")
    # 目标坐标 = 影像识别边 + 6 + clip_mm
    focus_target = image_recognition_coordinate + 6 + clip_mm
    go.only_y(the_front_tong_1, focus_target)
    time.sleep(sleep_time)
    # '''
    # 前提：尖端在原来与影像辨识边距离0有前进了10mm用于插入药板之间，
    # 夹具y方向前表面距离尖端为-11.5mm
    # 以影像辨识边为基础，此时夹具前表面为-1.5
    # 机械上药片板边缘比基础前6
    # y轴运动 5.5 - (-1.5) + 3
    # '''
    # y_move2 = 6 - 0.5 + clip_mm
    # go.only_y(0, y_move2)
    # time.sleep(sleep_time)

    # Z轴降低使得药片刚好高于卡位0.5mm
    # 获取当前夹具开口顶面
    body_tong_open_top = coordinate_converter.body_tong("open_top")
    # 夹取药板的下表面 =  开口顶面 - 药锡纸板厚度
    z_now1 = body_tong_open_top - plate_info["thickness"]
    # 目标点坐标 = 柜桶底表面 + 拱起量 + 预留值0.5mm
    hog_back_distance = ark_barrels_coordinates.get_plate_z("hog_back")
    z_target2 = z_baseboard + hog_back_distance + 0.5
    go.only_z(z_now1, z_target2)
    time.sleep(sleep_time)
    
    # Y轴和Y1轴慢速反向运动，把拉钩拉入药板槽，夹紧药板
    # y_y1(0, 7, 0, -7, 3360, 1100)
    y_y1(0, y_y1_mm, 0, -y_y1_mm, 4, 30)
    time.sleep(sleep_time)

    # y1轴可能还没有夹稳，增加一段使得确保夹稳
    go.only_y1(0, -7)
    time.sleep(sleep_time)

    # Y1轴持续拉回，将夹紧的药板完全拉入药板槽
    '''
    拉回到药片板y方向最后的边与药板支撑结构前表面在同一面上
    药板假设已处于边缘有5mm处夹在夹具内，那y方向，
    夹具最前面的坐标 + 药板长度 - 5mm ，即为以夹具前表面为基础的距离
    '''
    # 获取当前主体夹具前表面坐标
    the_front_tong = coordinate_converter.body_tong("the_front_y")
    # 药片板y方向最前沿坐标
    y1_now1 = the_front_tong + plate_info["length"] - clip_mm
    # 获取药板支撑结构前表面坐标
    y1_taeget = coordinate_converter.body("the_front_supporting_parts")
    go.only_y1(y1_now1, y1_taeget)
    time.sleep(sleep_time)

    # # y轴后退，保证推杆前表面在药柜影像辨识边之后约5mm，防撞
    # # 目标位置
    # y_taeget1 = image_recognition_coordinate - 5
    # # 推杆y方向最前端
    # y_now1 = coordinate_converter.body_push_rod("the_front")
    # # y1拉回与y后退同时启动
    # # y_y1(y_now1, y_taeget1, y1_now1, y1_taeget)
    # # time.sleep(sleep_time)
    # go.only_y(y_now1, y_taeget1)

    # y轴后退，保证xz运动安全，防撞
    go.xz_move_y_safe()
    time.sleep(sleep_time)

    result = take_correct(plate_info["length"])

    return result


def take_correct(length):
    """
    取药板的误差修正。因为设定的夹取距离 CLIP_MM 可能由于实际因素不是夹取到设定值。
    通过持续拉回药板触发限位开关获知误差值，修正使得药板y方向最前的边与药板支撑结构前表面在同一面上

    Parameters
    ----------
    length
        药板的长度

    Returns
    -------
    Returns
        修正成功返回True，否者返回False

    """
    standard_values = 111.368
    clip_mm = CLIP_MM

    # 拉回触发开关
    y1_origin = current_coordinates.get('motor_y1')             # 获取修正操作最初的位置

    # 快速到达准备点
    y1_target_ready = go.Y1_RANGE[0] + 5                       # 准备开始找位置的目标位
    move_mm_1 = y1_target_ready - y1_origin
    step_count_1, unit_step_1 = y1.move(move_mm_1)
    stop_mm_1 = round(step_count_1 * unit_step_1, 8)            # 计算到达准备点的运动距离
    current_coordinates.record('motor_y1', round(y1_origin + stop_mm_1, 8))     # 更新y1轴坐标

    # 开始找停止点
    y1_ready = current_coordinates.get('motor_y1')              # 获取目前主体的坐标
    y1_target_ws = go.Y1_RANGE[0] - 0.1                         # y1轴后极限位置设为目标
    move_mm_2 = y1_target_ws - y1_ready
    step_count_2, unit_step_2 = y1.move(move_mm_2, rpm_max_specify=100, where_stop=True)
    stop_mm_2 = round(step_count_2 * unit_step_2, 8)            # 计算触发前运动的距离

    # 更新y1轴坐标
    current_coordinates_y1 = y1_ready + stop_mm_2                   # 更新y1轴现有位置
    current_coordinates_y1 = round(current_coordinates_y1, 8)       # 限定小数点后8位
    print("480:更新后y1坐标：%s" % current_coordinates_y1)
    current_coordinates.record('motor_y1', current_coordinates_y1)  # 执行更新记录

    # 判断是否有效触发开关
    stop_mm = round(stop_mm_1 + stop_mm_2, 8)                   # 计算触发前总运动的距离
    move_mm = y1_target_ws - y1_origin
    if round(stop_mm - move_mm, 2) == 0:
        # 运动到最后都没有触发停止，修正失败
        return False
    else:
        # 正常触发了停止
        real_value = length - stop_mm
        correct_mm = round(standard_values - real_value, 8)
        print("修正的距离是是{}".format(correct_mm))

        # 获得修正参数后恢复基准位
        '''
        药片板y方向最后的边与药板支撑结构前表面在同一面上
        药板假设已处于边缘有5mm处夹在夹具内，那y方向，
        夹具最前面的坐标 + 药板长度 - 5mm ，即为以夹具前表面为基础的距离
        '''
        # 获取当前主体夹具前表面坐标
        the_front_tong = coordinate_converter.body_tong("the_front_y")
        # 药片板y方向最前沿坐标
        y1_now1 = the_front_tong + length - clip_mm - correct_mm
        # 获取药板支撑结构前表面坐标
        y1_target1 = coordinate_converter.body("the_front_supporting_parts")
        go.only_y1(y1_now1, y1_target1)

        return True


def do_back(medicine_num, row, line):
    """
    调用该函数实现放回药板

    Parameters
    ----------
    medicine_num
        药物的编号，具有唯一性
    row
        目前所在柜桶的行，0开始，顺轴正向增加
    line
        目前所在柜桶的列，0开始，顺轴正向增加
    """
    # ############################################## 常数值设定区域 ##############################################
    clip_mm = CLIP_MM           # 夹取药片边缘的宽度
    y_y1_mm = Y_Y1_MM  # y_y1相对运动夹稳药片板的运动距离
    sleep_time = 0.1              # 动作运动间隔的时间
    # ############################################################################################################

    # 1、获取需要的数据
    # 1.1 指定药物编号的json数据
    plate_info = get_plate_info(medicine_num)
    # 1.2 指定药柜的修正参数
    params_correction_xyz = params_correction.get_ark_barrels(row, line)
    # 1.3 柜桶相关信息
    ark_z_info = ark_barrels_coordinates.get_plate_z()

    # 2、xz双轴对齐
    # 2.0 判断药板是否在，并修正位置
    if not take_correct(plate_info["length"]):
        # 修正失败直接退出
        return False

    # 2.1 参数获取
    # x参数
    body_cusp_center_x, ark_barrels_x_center = \
        x_correct_coordinates(row, line, plate_info["ark_barrels"]["x"], params_correction_xyz[0], 0)
    # z参数
    body_cusp_center_z, z_baseboard = \
        z_correct_coordinates(row, line, ark_z_info, params_correction_xyz[2])
    z_cant_middle = body_cusp_center_z + 2.5            # 尖端斜面的中间高度偏下
    # 2.2 x轴夹子中心对齐柜桶中心,z轴尖端斜面的中间高度偏下与药板支撑面平齐
    # 同时进行节约时间
    go.xz(coordinate_now_x=body_cusp_center_x,
          coordinate_target_x=ark_barrels_x_center,
          coordinate_now_z=z_cant_middle,
          coordinate_target_z=z_baseboard)
    time.sleep(sleep_time)

    # 3、y轴修正，前进到 尖端 与 影像识别边 相距 0mm
    image_recognition_coordinate = y_correct(params_correction_xyz[1], 0)
    # y_correct(params_correction_xyz[1], 0)
    time.sleep(sleep_time)

    # 4、y轴前进12mm
    # 斜面顶最低药板，稍微将药板前推，便于后面抬高过程不碰到尖端
    go.only_y(0, 12)
    time.sleep(sleep_time)

    # 5、z轴抬高
    # 使得药板稍高于拱起0.5mm
    # 获取当前夹具开口顶面
    body_tong_open_top = coordinate_converter.body_tong("open_top")
    # 夹取药板的下表面 =  开口顶面 - 药锡纸板厚度
    z_now1 = body_tong_open_top - plate_info["thickness"]
    # 目标点坐标 = 柜桶底表面 + 拱起量 + 预留值0.5mm
    hog_back_distance = ark_barrels_coordinates.get_plate_z("hog_back")
    z_target2 = z_baseboard + hog_back_distance + 0.5
    go.only_z(z_now1, z_target2)
    time.sleep(sleep_time)

    # 6、y轴调整
    # 使得药板推出后，夹具前表面位于夹取药片clip_mm的位置
    # 关注点为一个虚空点，是夹药动作中，y_y1运动夹住药板时，此时夹具y方向的前表面
    # 通过调整y轴，使得该点位于这个状态，后续控制y1轴推出药板时刚好达到正确位置、
    # 6.1 获取当前关注点坐标
    # 计算尖端和关注点的距离
    the_front_tong = coordinate_converter.get("body", "tong", "the_front_y")
    cusp_center_y = coordinate_converter.get("body", "cusp_center")[1]
    cusp_2_focus = -(cusp_center_y - the_front_tong) - y_y1_mm
    # 当前坐标
    focus_now = coordinate_converter.body_cusp_center()[1] + cusp_2_focus
    # 6.2 获取关注点的目标坐标
    # 机械上药片板边缘比影像识别边前 6mm
    # 夹具夹取药板边缘 clip_mm
    # 目标坐标 = 影像识别边 + 6 + clip_mm
    focus_target = image_recognition_coordinate + 6 + clip_mm
    # 6.3 调用y轴控制调整位置
    go.only_y(focus_now, focus_target)
    time.sleep(sleep_time)

    # 7、y1推出药板
    # 推到松开前的位置，例如y_y1松开距离是7mm，那么y1走到0-7 = -7mm的位置
    # 获取当前y1的坐标
    current_coordinates_y1 = current_coordinates.get("motor_y1")
    # y1运动至 0 - y_y1_mm
    go.only_y1(current_coordinates_y1, 0 - y_y1_mm)
    time.sleep(sleep_time)

    # 8、y和y1配合运动松开夹具
    # Y轴和Y1轴慢速反向运动，松开药板
    y_y1(0, -y_y1_mm, 0, y_y1_mm, 4, 30)
    time.sleep(sleep_time)

    # 9、z轴下降
    # 使得夹具张口z方向中心与正常状态最底药板的相平
    # 该动作能保证放回的药板已低于拱起，防止y后退时把药板带出柜桶
    # 获取当前主体夹具开口中心
    body_tong_open_center = coordinate_converter.body_tong("open_center")
    # 最底药板的夹取中心 柜桶底表面 + 药锡纸板厚度/2 + 底下药板被上面影响抬起的高度1mm
    z_target1 = z_baseboard + plate_info["thickness"] / 2 + 1
    go.only_z(body_tong_open_center, z_target1)
    time.sleep(sleep_time)

    # 10、y后退
    # 完全退出到安全位置，保证xz运动安全，防撞
    go.xz_move_y_safe()
    time.sleep(sleep_time)

    return True


def throw_away():
    """
    将药板扔掉

    """
    sleep_time = 1  # 动作运动间隔的时间

    # 1、xz平面移动到扔药的位置
    target_z = 231.85
    target_x = 1205.7
    # 获取当前主体尖端的z坐标
    body_cusp_center_z = coordinate_converter.body_cusp_center()[2]
    # 获取当前主体的坐标x坐标
    body_cusp_center_x = coordinate_converter.body_cusp_center()[0]
    go.xz(coordinate_now_x=body_cusp_center_x,
          coordinate_target_x=target_x,
          coordinate_now_z=body_cusp_center_z,
          coordinate_target_z=target_z)
    time.sleep(sleep_time)

    # 2、y轴退后对准，y1轴归零实现丢弃药板
    distance_y = -30
    go.only_y(0, distance_y)
    # y1轴修正的作用就是归零
    y1_correct()
    time.sleep(sleep_time)

    # 3、y轴去回安全位置、
    go.xz_move_y_safe()
    time.sleep(sleep_time)

    # 4、x退回正常范围
    go.only_x(0, -30)
    time.sleep(sleep_time)

    return


def strike_drug_ready(parts_num, y_ready):
    """
    实现去到打药准备点,对于不同药物，准备工作都一样，
    使得xy面上打药的中心位于药板支撑面的y方向最前后退一段距离的位置和x方向中线，
    z高度控制在药片底面高于打药支撑面1mm处。

    Parameters
    ----------
    parts_num
        打药部件的编号
    y_ready
        药板支撑面的y方向最前超出中心的距离

    """
    sleep_time = 0.1          # 动作运动间隔的时间

    # 1、药夹尖端退后到打药装置最后，并有余量
    # 1.1 获取当前尖端y坐标
    body_cusp_center = coordinate_converter.body_cusp_center()          # 一次提取xyz，后续需要直接获取
    body_cusp_center_y = body_cusp_center[1]
    # 1.2 获取打药装置最后的y坐标
    the_back_strike_drug_parts = constant_coordinates.get("strike_drug_parts", str(parts_num), "the_back")
    print(body_cusp_center_y, the_back_strike_drug_parts)
    # 1.3 退后到相差25mm的位置
    go.only_y(body_cusp_center_y, (the_back_strike_drug_parts - 25))
    time.sleep(sleep_time)

    # 2、伸出的推杆最底部要高于打药装置最顶，并有余量
    # 2.1 获取当前推杆最底部的z坐标
    the_bottom_push_rod = coordinate_converter.body_push_rod("the_bottom")
    # 2.2 获取打药装置最顶的z坐标
    the_top_strike_drug_parts = constant_coordinates.get("strike_drug_parts", str(parts_num), "the_top")
    print(the_bottom_push_rod, the_top_strike_drug_parts)
    # 2.3 调整高度，余量20mm
    go.only_z(the_bottom_push_rod, (the_top_strike_drug_parts + 20))
    time.sleep(sleep_time)

    # 3、移动x轴让药片中心与打药孔中心对齐
    # 3.1 获取当前药片中心，即夹子中心x坐标
    body_cusp_center_x = body_cusp_center[0]
    # 3.2 获取打药孔x坐标
    # 一次提取xyz坐标，后续需要直接获取
    strike_drug_parts_center = constant_coordinates.get("strike_drug_parts", str(parts_num), "center")
    strike_drug_parts_center_x = strike_drug_parts_center[0]
    print(body_cusp_center_x, strike_drug_parts_center_x)
    # 3.3 移动x轴对齐
    go.only_x(body_cusp_center_x, strike_drug_parts_center_x)
    time.sleep(sleep_time)

    # 4、降低z轴让药片底面与打药支撑面平齐，稍微高一点
    # 4.1 获取当前药片支撑面的z坐标
    tablet_plate_bearing_surface = coordinate_converter.body("tablet_plate_bearing_surface")
    # 4.2 获取打药孔面的z坐标
    strike_drug_parts_center_z = strike_drug_parts_center[2]
    print(tablet_plate_bearing_surface, strike_drug_parts_center_z)
    # 4.3 移动z轴对齐，稍微高2mm
    go.only_z(tablet_plate_bearing_surface, (strike_drug_parts_center_z + 3))
    time.sleep(sleep_time)

    # 5、y轴推出让药片最前端超出打药孔中心一定距离
    # 5.1 获取当前药片支撑装置的最前面y坐标，默认此为药片最前端
    the_front_supporting_parts = coordinate_converter.body("the_front_supporting_parts")
    # 5.2 获取打药孔中心的y坐标
    strike_drug_parts_center_y = strike_drug_parts_center[1]
    print(the_front_supporting_parts, strike_drug_parts_center_y)
    # 5.3 移动y轴对准位置
    go.only_y(the_front_supporting_parts, strike_drug_parts_center_y + y_ready)
    time.sleep(sleep_time)

    # 该下降修改到打药的之前才下降，打完立马上升
    # # 5.4 移动z轴，稍微降1mm
    # go.only_z(0, -2)
    # time.sleep(sleep_time)

    # 6、至此打药前的准备完成，到达指定位置，返回函数
    return


def strike_drug_finish(parts_num):
    """
    打完药，需要退出到安全位置，避免后续操作中推杆撞到其他机械部件
    前提：打药结束后，药板拉回至打药准备状态

    Parameters
    ----------
    parts_num
        打药部件的编号

    """
    # ############################################## 常数值设定区域 ##############################################
    sleep_time = 0.1        # 动作运动间隔的时间
    # ############################################################################################################
    # 1、药夹尖端退后到打药装置最后，并有余量
    # 1.1 获取当前尖端y坐标
    body_cusp_center = coordinate_converter.body_cusp_center()          # 一次提取xyz，后续需要直接获取
    body_cusp_center_y = body_cusp_center[1]
    # 1.2 获取打药装置最后的y坐标
    the_back_strike_drug_parts = constant_coordinates.get("strike_drug_parts", str(parts_num), "the_back")
    print(body_cusp_center_y, the_back_strike_drug_parts)
    # 1.3 退后到相差25mm的位置
    go.only_y(body_cusp_center_y, (the_back_strike_drug_parts - 25))
    time.sleep(sleep_time)

    # 2、伸出的推杆最底部要高于打药装置最顶，并有余量
    # 2.1 获取当前推杆最底部的z坐标
    the_bottom_push_rod = coordinate_converter.body_push_rod("the_bottom")
    # 2.2 获取打药装置最顶的z坐标
    the_top_strike_drug_parts = constant_coordinates.get("strike_drug_parts", str(parts_num), "the_top")
    print(the_bottom_push_rod, the_top_strike_drug_parts)
    # 2.3 调整高度，余量20mm
    go.only_z(the_bottom_push_rod, (the_top_strike_drug_parts + 20))
    time.sleep(sleep_time)

    # 3、x方向移动
    # 保证body整体x方向与打药装置不重叠
    distance_x = 90         # 该距离能保证安全
    go.only_x(0, distance_x)
    time.sleep(sleep_time)

    return


def strike_drug_do(medicine_num, y_ready, num_start, strike_num, direction):
    """
    针对药物移动控制打药。
    注意y方向移动只运动y1轴，且认为药板边缘与支撑面边缘平齐。

    Parameters
    ----------
    medicine_num
        药物的编号，具有唯一性
    y_ready
        药板支撑面的y方向最前超出中心的距离
    num_start
        开始的数量，也就是要打的第一粒是药板的第几粒。
        打药顺序：优先走y1，该列打完了移动x换下一列。走蛇形。
    strike_num
        需要打出药的数量
    direction
        药板的正反方向。
        1：代表正向，指的是夹住较宽的边，左上角第一粒药位于窄边
        0：代表反向，状态与1相反。

    """
    # ############################################## 常数值设定区域 ##############################################
    # clip_mm = CLIP_MM       # 夹取药片边缘的宽度
    sleep_time = 0.1        # 动作运动间隔的时间
    # ############################################################################################################
    """
    控制实现的逻辑：
    将固定的打药头和运动的药板在运动控制中转换，变为
    运动的是打药头，不动的是药板，从而计算出需要移动的x，y距离，
    该值加一个 - 号便是对应药板需要运动的 x， y1的值。
    """
    # 0、获取需要的数据
    # 指定药物编号的json数据
    plate_info = get_plate_info(medicine_num)

    # 1、判断指定的打药数，药板剩余数是否足够
    # (药板粒数 - 开始的数量 + 1) ？> 需要打的数量
    if (plate_info["num"] - num_start + 1) < strike_num:
        # 数量不足
        print("\n")
        print("指定的打药数，目前药板数量不足，请确认。")
        print("\n")
        return False
    else:
        # 数量充足，继续执行打药
        center_list = []  # 创建一个记录打药中心坐标的列表
        print(plate_info["medicine_distribution"]["regularity"])
        if plate_info["medicine_distribution"]["regularity"] == 1:
            # 药板分布均匀
            # 根据药板方向确定左上角第一粒药中心坐标
            if direction == 1:
                # 正向，窄边
                origin_center = plate_info["medicine_distribution"]["center"]["narrow_side"]
            else:
                # 反向，宽边
                origin_center = plate_info["medicine_distribution"]["center"]["broad_side"]
            # 获取中心点距离和数量
            x_sum = plate_info["medicine_distribution"]["center"]["x_sum"]
            x_distance = plate_info["medicine_distribution"]["center"]["x_distance"]
            y_sum = plate_info["medicine_distribution"]["center"]["y_sum"]
            y_distance = plate_info["medicine_distribution"]["center"]["y_distance"]
            # 生成中心点列表
            for i in range(x_sum):
                for j in range(y_sum):
                    if (num_start-1) <= (i * y_sum + j) < (num_start+strike_num-1):
                        # 记录目标中心坐标
                        center_list.append([origin_center[0] + i * x_distance, origin_center[1] + j * y_distance])
                    else:
                        # 非目标计算值，跳过
                        continue
        else:
            # 药板分布不均匀，中心坐标照搬记录，不需要计算
            for i in range(len(plate_info["medicine_distribution"]["center"]["list"])):
                if (num_start-1) <= i < (num_start+strike_num-1):
                    # 记录目标中心坐标
                    center_list.append(plate_info["medicine_distribution"]["center"]["list"][i])
                else:
                    # 非目标计算值，跳过
                    continue
        print("中心坐标：%s" % center_list)
        time.sleep(sleep_time)

        length = plate_info["length"]
        width = plate_info["width"]
        # 运动的范围
        x_range = [0, width]
        y1_range = [0, length]

        # 初始化指针坐标
        pointer_xy = [width/2, y_ready]

        for i in range(strike_num):

            # 1、去到药的中心
            # 判断指针移动的目标在药板范围内
            if x_range[0] < center_list[i][0] < x_range[1] and y1_range[0] < center_list[i][1] < y1_range[1]:
                # 1.1 x轴调整
                x_move = -(center_list[i][0] - pointer_xy[0])
                go.only_x(0, x_move)
                # 更新指针坐标
                pointer_xy[0] = center_list[i][0]
                time.sleep(sleep_time)

                # 1.2 y1轴调整
                # 由于药板的y正方向与运动控制的刚好相反，所以不需要添加负号
                y1_move = center_list[i][1] - pointer_xy[1]
                go.only_y1(0, y1_move)
                # 更新指针坐标
                pointer_xy[1] = center_list[i][1]
                time.sleep(sleep_time)

                # 2、打药装置打药
                go.only_z(0, -2)             # 到位后降低
                strike.do()
                time.sleep(sleep_time)
                go.only_z(0, 2)             # z轴抬高避免卡板


            # 超出药板范围
            else:
                print("\n")
                print("打击点目标运动值超出药板范围，请检查。")
                print("\n")
                return False
        # y1恢复初态
        y1_move_finish = y_ready - pointer_xy[1]
        go.only_y1(0, y1_move_finish)
        time.sleep(sleep_time)
        return True


def strike_drug(medicine_num, parts_num, num_start, strike_num, direction):
    """
    调用实现打药全流程，包含：
    准备 -- 打药 -- 结束

    Parameters
    ----------
    medicine_num
        药物的编号，具有唯一性
    parts_num
        打药部件的编号
    num_start
        开始的数量，也就是要打的第一粒是药板的第几粒。
        打药顺序：优先走y1，该列打完了移动x换下一列。走蛇形。
    strike_num
        需要打出药的数量
    direction
        药板的正反方向。
        1：代表正向，指的是夹住较宽的边，左上角第一粒药位于窄边
        0：代表反向，状态与1相反。

    """
    # ############################################## 常数值设定区域 ##############################################
    # clip_mm = CLIP_MM       # 夹取药片边缘的宽度
    sleep_time = 0.1        # 动作运动间隔的时间
    y_ready = 10            # 药板支撑面的y方向最前超出中心的距离
    # ############################################################################################################
    # 1、打药准备
    # 控制药板去到打药位置待定
    strike_drug_ready(parts_num, y_ready)
    time.sleep(sleep_time)

    # 2、执行打药
    # 按照不同药，从文件获取药中心坐标，
    strike_drug_do(medicine_num, y_ready, num_start, strike_num, direction)
    time.sleep(sleep_time)

    # 3、完毕退出
    # 打完药，需要退出到安全位置，避免后续操作中推杆撞到其他机械部件
    strike_drug_finish(parts_num)
    time.sleep(sleep_time)

    return


def setup_main():
    """
    作为主函数时的初始化

    """
    z_setup_return = z.setup()
    if not z_setup_return:
        print('Z轴初始化失败')

    x_setup_return = x.setup()
    if not x_setup_return:
        print('X轴初始化失败')

    y_setup_return = y.setup()
    if not y_setup_return:
        print('Y轴初始化失败')

    y1_setup_return = y1.setup()
    if not y1_setup_return:
        print('Y1轴初始化失败')

    x1_setup_return = x1.setup()
    if not x1_setup_return:
        print('X1轴初始化失败')

    return True


# 循环部分
def loop():
    # strike_drug(6924168200093, parts_num=1, num_start=4, strike_num=4, direction=1)
    # strike_drug_do(6924168200093, y_ready=10, num_start=4, strike_num=4, direction=1)
    # # ========= 测试
    # stop_mm = 10.04
    # move_mm = 10
    # print(round(stop_mm - move_mm, 1) == 0)

    # ============ 测试take_correct
    take_correct()

# 结束释放
def destroy():
    z.destroy()
    y.destroy()
    x.destroy()
    y1.destroy()
    x1.destroy()
    return


# 如果该程序为主程序，程序在此开始运行，若不是不运行，该文件只做函数定义
if __name__ == '__main__':  # Program start from here
    setup_return = setup_main()
    if setup_return:
        print('始化成功')
    try:
        loop()
    except KeyboardInterrupt:  # 当按下 'Ctrl+C', 子函数 destroy()将会运行，用于停止退出
        print("程序已停止退出...")
        destroy()
