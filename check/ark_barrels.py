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
import JSON.current_coordinates as current_coordinates
import JSON.params_correction as params_correction
import motor.go as go
import image.camera as camera
import motor.y_drive as y
import motor.x_drive as x
import motor.z_drive as z
import motor.x1_drive as x1
import motor.y1_drive as y1
import cv2
import os
import json
import time
import numpy as np
import matplotlib.pyplot as plt

debug = 0
sleep_time = 0.1
# ############################ 常数值设定区域 ############################
current_path = os.path.dirname(__file__)  # 获取本文件的路径
picture_dir_path = current_path + "/../image/picture/"  # 加上目标文件的相对路径
ark_barrel_img_path = picture_dir_path + "video1/250.jpg"  # 柜桶图片的绝对路径
tong_img_path = picture_dir_path + "video1/400.jpg"  # 夹子图片的绝对路径

OFFSET_DECIMALS = 8              # offset的小数位数，8位

ARK_FIND_POS_LINE = 1632
ARK_THRE = 160
ARK_POS_RANGE = [220, 480, 2020, 2320]

TONG_FIND_POS_LINE = 775
TONG_THRE = 60
TONG_POS_RANGE = [18, 374, 2167, 2421]

# ########################################################################


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


def tong_center():
    """
    识别夹具中心的偏移量。param_correction函数需要该参数

    Returns
    -------
    return
        off_set-相对于x轴坐标，偏负方向为-，偏正方向为+，单位为mm。

    """
    # 0、调整x1,y1轴坐标
    go.only_x1(68)                  # 取药夹打开到最大宽度，68
    y1_correct()                    # y1轴修正，达到最前端

    # 1、获取夹具图像
    video_tong = camera.Video(camera.DEVICE_NAME_TONG)                          # 创建夹具图像实例
    video_tong.set_parm(focus_absolute=camera.FOCUS_ABSOLUTE_TONG,              # 设置成像参数
                        exposure_absolute=camera.EXPOSURE_ABSOLUTE_TONG)
    tong_img, picture_dir_path = video_tong.take_photo(picture_name="tong_center_offset",    # 拍照
                                                       resolution=camera.RESOLUTION_TONG)
    # 2、识别中心线
    grimg1 = cv2.cvtColor(tong_img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(picture_dir_path + '/tong_center_offset_gray.jpg', grimg1)
    pos2, pos4 = find_pos(grimg1=grimg1,
                          line=TONG_FIND_POS_LINE,
                          thre=TONG_THRE,
                          range=TONG_POS_RANGE)          # 识别出两条线的坐标
    mid_tong = (pos4 + pos2) / 2
    print('夹具中间线坐标：', mid_tong)

    if debug:
        plt.figure()
        # plt.subplot(1, 2, 2)
        plt.imshow(tong_img, cmap='gray')
        plt.hlines(pos2, 0, tong_img.shape[1] - 1, colors='r')
        plt.hlines(pos4, 0, tong_img.shape[1] - 1, colors='r')
        plt.vlines(TONG_FIND_POS_LINE, 0, tong_img.shape[0] - 1, colors='g')
        plt.title('Pos2 Pos4 ' + str(pos2) + ',' + str(pos4) + ',mid=' + str(mid_tong))
        plt.show()

    # 3、将偏移坐标转换为实际数值mm
    coefficient = camera.COEFFICIENT_TONG
    offset_pixel = mid_tong - camera.RESOLUTION_TONG[1]/2
    offset_mm = coefficient * offset_pixel
    offset_mm = round(offset_mm, OFFSET_DECIMALS)               # 限定小数点后8位

    return offset_mm


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
    if 0 <= num_center < ark_barrels_x["num_center"]:  # 保证指定柜桶在记录的范围内
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


def y_correct(correction, reserved_distance=5):
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


def get_ark_offset(tong_center_offset):
    """
    拍照识别柜桶，获取三轴的偏移量

    Parameters
    ----------
    tong_center_offset
        夹具中心线的偏移量。
        相对于x轴坐标，偏负方向为-，偏正方向为+，单位为mm。

    Returns
    -------
    return
        x_offset-相对于x轴坐标，偏负方向为-，偏正方向为+，单位为mm
        z_offset-相对于z轴坐标，偏负方向为-，偏正方向为+，单位为mm
        y_offset-相对于y轴坐标，偏负方向为-，偏正方向为+，单位为mm
    """
    # 1、获取柜桶图像
    video_ark = camera.Video(camera.DEVICE_NAME_ARK)                          # 创建柜桶图像实例
    video_ark.set_parm(focus_absolute=camera.FOCUS_ABSOLUTE_ARK,              # 设置成像参数
                       exposure_absolute=camera.EXPOSURE_ABSOLUTE_ARK)
    ark_img, picture_dir_path = video_ark.take_photo(picture_name="ark_center_offset",    # 拍照
                                                     resolution=camera.RESOLUTION_ARK)
    # 2、识别中心线
    grimg1 = cv2.cvtColor(ark_img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(picture_dir_path + '/ark_center_offset_gray.jpg',grimg1)
    pos2, pos4 = find_pos(grimg1=grimg1,
                          line=ARK_FIND_POS_LINE,
                          thre=ARK_THRE,
                          range=ARK_POS_RANGE)          # 识别出两条线的坐标
    mid_ark = (pos4 + pos2) / 2
    print('柜桶中间线坐标：', mid_ark)

    if debug:
        plt.figure()
        # plt.subplot(1, 2, 2)
        plt.imshow(ark_img)
        plt.hlines(pos2, 0, ark_img.shape[1] - 1, colors='g')
        plt.hlines(pos4, 0, ark_img.shape[1] - 1, colors='g')
        plt.title('Pos2 Pos4 ' + str(pos2) + ',' + str(pos4) + ',mid=' + str(mid_ark))
        plt.show()

    # 3、将偏移坐标转换为实际数值mm
    coefficient = camera.COEFFICIENT_ARK
    offset_pixel = mid_ark - camera.RESOLUTION_ARK[1]/2
    x_offset = coefficient * offset_pixel - tong_center_offset
    x_offset = round(x_offset, OFFSET_DECIMALS)         # 限定小数点后8位

    return x_offset


def param_correction(medicine_num, row, line, tong_center_offset=0, num_center=0):
    """
    实现指定柜桶的xz坐标数据的获取并更新到对应的json文件中

    Parameters
    ----------
    medicine_num
        药物的编号，具有唯一性
    row
        目前所在柜桶的行，0开始，顺轴正向增加
    line
        目前所在柜桶的列，0开始，顺轴正向增加
    tong_center_offset
        夹具识别中，夹具中心相对于图像中心的偏移量。
        相对于x轴坐标，偏负方向为-，偏正方向为+，单位为mm。
    num_center
        目标药板位于该柜桶的第几列，顺x轴正方向增加,0 or 1，默认是0

    Returns
    -------
    """
    # 1、根据标准记录移动到指定柜桶的位置
    # 1.1 指定药物编号的json数据
    plate_info = get_plate_info(medicine_num)
    params_correction_xyz = params_correction.get_ark_barrels(row, line)        # 指定药柜的修正参数
    # 1.2 柜桶相关信息
    ark_z_info = ark_barrels_coordinates.get_plate_z()
    ark_y_info = ark_barrels_coordinates.get_plate_y()

    # 1.3 x，z轴对准参数获取
    # x轴对药板中心
    body_cusp_center_x, ark_barrels_x_center = \
        x_correct_coordinates(row, line, plate_info["ark_barrels"]["x"], params_correction_xyz[0], num_center)
    # z轴对药板支撑面
    body_cusp_center_z, z_baseboard = \
        z_correct_coordinates(row, line, ark_z_info, params_correction_xyz[2])
    z_base_2_target = z_baseboard - 15                                       # 对准降低保证识别线在镜头中心位置

    # 1.4 x轴修正对齐，夹子中心对齐柜桶中心,z轴修正对齐，尖端底部与药板支撑面平齐
    # 同时进行节约时间
    go.xz(coordinate_now_x=body_cusp_center_x,
          coordinate_target_x=ark_barrels_x_center,
          coordinate_now_z=body_cusp_center_z,
          coordinate_target_z=z_base_2_target)
    time.sleep(sleep_time)

    # 1.5 y轴修正，前进到 尖端 与 影像识别边 相距 5mm
    image_recognition_coordinate = y_correct(params_correction_xyz[1], 5)
    time.sleep(sleep_time)
    # =========================================第一步完成=========================================

    # 2、拍照识别返回偏差值x_offset, z_offset，y_offset
    x_offset = get_ark_offset(tong_center_offset)
    # =========================================第二步完成=========================================

    # 3、更新param_correction.json文件对应的柜桶数据中
    print("修改坐标增量为：%s" % [x_offset, 0, 0])
    # params_correction.record_ark_barrels(row, line, [x_offset, 0, 0])
    # =========================================第三步完成=========================================

    return


# ############################### 函数说明 ###############################
# 调用运行将实现走一遍柜桶所在位置确保xyz轴工作正常且柜桶位置正确
# ########################################################################
def run_all():
    ark_barrels_all = ark_barrels_coordinates.get_all()  # 获取柜桶坐标文件中所用内容
    ark_barrels_sum = len(ark_barrels_all)  # 得出柜桶总数，用于控制遍历柜桶
    ark_barrels_keys = list(ark_barrels_all.keys())  # 获取所有key作为列表
    print(ark_barrels_sum)
    for i in range(ark_barrels_sum):  # 循环走一遍所有柜桶
        target_coordinates_xyz = ark_barrels_all[ark_barrels_keys[i]]  # 获取目标柜桶的坐标
        # 获取目前主体的坐标
        current_coordinates_body = coordinate_converter.body_cusp_center()
        print("前往%s号柜桶，该柜桶坐标为%s，目前body所在坐标为%s"
              % (ark_barrels_keys[i], target_coordinates_xyz, current_coordinates_body))  # 打印相关信息
        go.only_y(current_coordinates_body[1], target_coordinates_xyz[1])  # Y轴运动
        go.only_x(current_coordinates_body[0], target_coordinates_xyz[0])  # X轴运动
        # Z轴做一个往返动作，意指顺利进入拿药位置
        go.only_z(current_coordinates_body[2], target_coordinates_xyz[2])
        go.only_z(target_coordinates_xyz[2], current_coordinates_body[2])
        print("body的坐标更新为：%s" % coordinate_converter.body_cusp_center())  # 打印信息
    go.wait()  # 检查结束后去工作等待点
    return 'success'


def find_pos(grimg1, line, thre, range):
    """
    find landmark position pos1, pos3 from color image
    suggested thre 230-240 , can change due to different light conditions
    allpos1 and allpos3 are lists of all/most important landmark,
    can be used to find other locations due to noisy images

    Parameters
    ----------
    grimg1
        输入的完整图片
    line
        需要识别的线条的位置坐标
    thre
        阈值，有两个模式：
        白光阈值，建议230-240，
        黑暗阈值，建议50-60.
    range
        pos1和3的范围，[pos1_l, pos1_r, pos3_l, pos3_r]

    Returns
    -------
    [返回]
        左标记点坐标，右标记点坐标
    """

    # 图像灰度化

    # cv2.namedWindow('GRAY', cv2.WINDOW_NORMAL)
    # cv2.imshow('GRAY', grimg1)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # 根据阈值选择关注的颜色
    # 关注黑色
    if thre < 125:
        segline = grimg1[:, line] < thre  # can change 1550 to other positions, 750 for 800 x image
    # 关注白色
    else:
        segline = grimg1[:, line] > thre  # can change 1550 to other positions, 750 for 800 x image

    if debug:
        plt.figure()
        plt.subplot(221)
        plt.plot(grimg1[:, line])
        plt.subplot(222)
        plt.plot(segline[:-2])
        plt.subplot(223)
        plt.plot(~segline[2:])
        plt.subplot(224)
        plt.plot(segline[:-2] & (~segline[2:]))
        plt.show()

    # 跳变点识别
    # 黑色关注下降沿
    if thre < 125:
        allpos1 = np.where(segline[:-1] & (~segline[1:]) == True)[0]    # 下降沿
    # 白色关注上升沿
    else:
        allpos1 = np.where(~segline[:-1] & (segline[1:]) == True)[0]    # 上升沿
    allpos1t = [x for x in allpos1 if range[0]< x < range[1]]  # stable y pos
    # allpos1t = [x for x in allpos1 if x > 30]  # stable y pos
    # print(allpos1)
    pos1 = allpos1t[0]
    if False and pos1 < 500:  # can be adjusted
        pos1 = allpos1[1]
    # plt.figure();plt.plot(grimg1[:,1550]);plt.show()
    if debug:
        print(allpos1t)

    # 黑色关注上升沿
    if thre < 125:
        allpos3 = np.where(~segline[:-1] & (segline[1:]) == True)[0]  # 上升沿
    # 白色关注下降沿
    else:
        allpos3 = np.where(segline[:-1] & (~segline[1:]) == True)[0]  # 下降沿

    allpos3t = [x for x in allpos3 if range[2]< x < range[3]]  # stable y pos
    # allpos3t = [x for x in allpos3 if x > 900]  # stable y pos
    if debug:
        print(allpos3t)
    pos3 = allpos3t[-1]
    if False and pos3 < 1600:
        pos3 = allpos3[3]
    # print(pos1,pos3)
    # pos1 and pos3 are first two landmark position
    # allpos1 and allpos2 contains all posible positions to be checked if other noisy image appears

    if debug:
        print(pos1, pos3)
        plt.figure()
        # plt.subplot(1, 2, 1)
        plt.imshow(grimg1)
        for pos_l in allpos1t:
            plt.hlines(pos_l, 0, grimg1.shape[1] - 1, colors='r')
        for pos_r in allpos3t:
            plt.hlines(pos_r, 0, grimg1.shape[1] - 1, colors='r')
        plt.vlines(line, 0, grimg1.shape[0] - 1, colors='g')
        plt.show()

    return pos1, pos3


def comparison():
    ark_barrel_img = cv2.imread(ark_barrel_img_path)
    # tong_img = cv2.imread(tong_img_path)

    # cv2.namedWindow('250', cv2.WINDOW_NORMAL)
    # cv2.imshow('250', ark_barrel_img_cut)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    pos1, pos3 = find_pos(ark_barrel_img, ARK_FIND_POS_LINE, 230)
    mid_ark_barrel = (pos3 + pos1) / 2
    print('钣金中间线：', mid_ark_barrel)

    # pos2, pos4 = findpos(tong_img, TONG_FIND_POS_LINE, 60)
    # mid_tong = (pos4 + pos2) / 2
    # print('夹具中间线：', mid_tong)

    if debug:
        plt.figure()
        # plt.subplot(1, 2, 1)
        plt.imshow(ark_barrel_img)
        plt.hlines(pos1, 0, ark_barrel_img.shape[1] - 1, colors='r')
        plt.hlines(pos3, 0, ark_barrel_img.shape[1] - 1, colors='r')
        plt.vlines(ARK_FIND_POS_LINE, 0, ark_barrel_img.shape[0] - 1, colors='g')
        plt.title('Pos1 Pos3 ' + str(pos1) + ',' + str(pos3) + ',mid=' + str(mid_ark_barrel))

        # plt.subplot(1, 2, 2)
        # plt.imshow(tong_img)
        # plt.hlines(pos2, 0, tong_img.shape[1] - 1, colors='g')
        # plt.hlines(pos4, 0, tong_img.shape[1] - 1, colors='g')
        # plt.title('Pos2 Pos4 ' + str(pos2) + ',' + str(pos4) + ',mid=' + str(mid_tong))
        plt.show()

    # tong_img = cv2.imread(tong_img_path)
    # tong_img_cut = tong_img[0:1200, 0:400]
    # pos2,pos4 = findpos1(tong_img_cut, 50)
    # print('药夹中间线：',(pos2+pos4) / 2)
    # b = (pos2+pos4) / 2

    # plt.figure();plt.imshow(tong_img_path)
    # plt.hlines(pos2,0,tong_img_path.shape[1]-1,colors='b')
    # plt.hlines(pos4,0,tong_img_path.shape[1]-1,colors='b')

    # plt.title(str((pos3+pos1)/2)+','+str((pos2+pos4)/2));plt.show()

    # if a>(b+5 ) or a>(b-5):
    #     print('success')


# 初始化设定
def setup():
    z_setup_return = z.setup()
    if not z_setup_return:
        print('Z轴初始化失败')

    x_setup_return = x.setup()
    if not x_setup_return:
        print('X轴初始化失败')

    y_setup_return = y.setup()
    if not y_setup_return:
        print('Y轴初始化失败')

    x1_setup_return = x1.setup()
    if not x1_setup_return:
        print('X1轴初始化失败')

    y1_setup_return = y1.setup()
    if not y1_setup_return:
        print('Y1轴初始化失败')

    return True


# 循环部分
def main():
    # segline = [0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 1]
    # print(np.where(segline)[0])

    # x = -0.068360000000000004
    # x = round(x, 8)
    # print("修改坐标增量为：%s" % [x, 0, 0])

    offset = tong_center()
    print("夹具的中心偏差值为：%smm" % offset)
    offset1 = 0.20444

    tong_center_offset = offset
    x_offset = get_ark_offset(tong_center_offset)
    print("return后：%s" % x_offset)
    print("修改坐标增量为：%s" % x_offset)

    #
    # video_1 = camera.Video("video1")
    #
    # video_1.set_parm(exposure_absolute=camera.EXPOSURE_ABSOLUTE_1)
    # # video_1.take_photo()
    # i = 10
    # while i <= 100:
    #     video_1.set_parm(focus_absolute=i)
    #     video_1.take_photo(str(i), [3264, 2448])
    #     i += 10
    #
    # i = 100
    # while i <= 300:
    #     video_1.set_parm(focus_absolute=i)
    #     video_1.take_photo(str(i), [3264, 2448])
    #     i += 50
    #
    # i = 300
    # while i <= 1000:
    #     video_1.set_parm(focus_absolute=i)
    #     video_1.take_photo(str(i), [1600, 1200])
    #     i += 100
    # video_1.show()
    # print(result.read())
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
