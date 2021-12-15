#!/usr/bin/env python 
# -*- coding:utf-8 -*-
"""
面板基准测定。由于机械安装的误差，移动主体拍摄柜桶的镜头2到柜桶识别边的物距并不是固定的。
对于不同机子安装，同一个机子不同位置的柜桶，都有可能是不同的。
因此在进行柜桶 xz位置修正前，需要先进行y轴的调整。
原则是通过识别基准柜桶上二维码的对角线像素距离，计算出实际物距，由此判断偏移了多少。
原理是摄像头成像遵从近大远小，且成线性比例。
主要函数：
param_correction：获取y的偏移量并更新
make_predict_model：预测模型建立
"""
#########################################################
#   File name:  ark_barrels.py
#      Author:  钟东佐
#       Date        ||      describe
#   2021/9/29       ||   创建采样数据

#########################################################
import JSON.coordinate_converter as coordinate_converter
import JSON.medicine_plate_info as medicine_plate_info
import JSON.ark_barrels_coordinates as ark_barrels_coordinates
import JSON.current_coordinates as current_coordinates
import JSON.params_correction as params_correction
import motor.go as go
import image.camera as camera
import image.qr_code as qr_code
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
from sklearn.linear_model import LinearRegression

debug = 1
sleep_time = 0.1
# ############################ 常数值设定区域 ############################
current_path = os.path.dirname(__file__)  # 获取本文件的路径
# picture_dir_path = current_path + "/../image/picture/"  # 加上目标文件的相对路径


OFFSET_DECIMALS = 8              # offset的小数位数，8位


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


def x_correct_coordinates(row, line, correction):
    """
    计算获取 完成 将镜头2 x方向中线修正，使之对齐目标标准柜桶二维码的中心 的坐标

    Parameters
    ----------
    row
        目前所在柜桶的行
    line
        目前所在柜桶的列
    correction
        坐标修正，含正负，加法使用

    """
    # 获取目标柜桶的坐标
    target_coordinates_x = ark_barrels_coordinates.get(row, line)[0]
    # 获取当前主体的坐标
    camera_x = coordinate_converter.camera(2)[0]
    # 目标位置 = 目标柜桶x坐标 + 修正量
    ark_barrels_x_center = target_coordinates_x + correction
    return camera_x, ark_barrels_x_center


def z_correct_coordinates(row, line, ark_barrels_z_dis, correction):
    """
    计算获取完成 z轴对齐，使得镜头2 与 标准柜桶二维码平齐
    Parameters
    ----------
    row
        目前所在柜桶的行
    line
        目前所在柜桶的列
    ark_barrels_z_dis
        柜桶z方向上的信息。
        "qr_code"：标准柜桶二维码z中线坐标。
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
    ark_barrels_z = ark_barrels_coordinates.get(row, line)[2]
    # 获取当前镜头2的z坐标
    camera_z = coordinate_converter.camera(2)[2]
    # 目标位置 = 目标柜桶z坐标 + 底板表面相对量 + 修正量
    z_qr_code = ark_barrels_z + ark_barrels_z_dis["qr_code"] + correction
    # print("168：完成修正z对准药片板支撑铁片的坐标运算")
    return camera_z, z_qr_code


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


def get_y_offset():
    """
    分析图像并计算返回y方向的偏移量

    """
    # 1、获取柜桶图像
    video_qr = camera.Video(camera.DEVICE_NAME_QR)                      # 创建柜桶二维码图像实例
    video_qr.set_parm(focus_absolute=camera.FOCUS_ABSOLUTE_QR,          # 设置成像参数
                      exposure_absolute=camera.EXPOSURE_ABSOLUTE_QR)
    qr_img, picture_dir_path = video_qr.take_photo(picture_name="ark_qr_offset",        # 拍照
                                                   resolution=camera.RESOLUTION_QR)

    # 2、分析图片
    opposite_dis, data = qr_code.opposite_point_dis(file_name="ark_qr_offset.jpg", dir_path=picture_dir_path + '/')
    # 正确识别，进行模型预测
    if opposite_dis:
        # 获取模型数据
        predictions = np.load('predictions_model.npy', allow_pickle=True).item()
        intercept = round(predictions['intercept'], 8)                              # 截距
        coefficient = round(predictions['coefficient'][0], 8)                       # 系数，斜率
        y_offset = round(opposite_dis * coefficient + intercept, 8)                 # 计算物距
        return y_offset
    # 识别错误，无法预测
    else:
        if debug:
            print("图像识别出错，无法获取y方向偏移量")
        return False


def linear_model_main(x_para=None, y_para=None, predict_value=None, show=None):
    """
    通过线性回归获取变化，计算输入值predict_value的函数值并返回相关数据。

    Parameters
    ----------
    x_para
        x轴的数据，有要求输入的是二维数组，默认diagonal_len_list.npz中获取
    y_para
        y轴的数据，一维数组，默认diagonal_len_list.npz中获取
    predict_value
        需要预测的x轴坐标，不输入则没有predicted_value
    show
        置1展示散点图以及线性回归线，默认不展示

    Returns
    -------
    Returns
        线性方程的相关数据
        intercept：截止点
        coefficient：一次函数斜率
        predicted_value：预测的函数值

    """
    # 获取x，y数据
    if x_para:
        # 函数调用有指定
        x_parameters = x_para
        y_parameters = y_para
    else:
        # 没有指定使用默认的diagonal_len_list.npz文件
        if os.path.exists(current_path + '/diagonal_len_list.npz'):
            diagonal_len_list = np.load(current_path + '/diagonal_len_list.npz')
            # print(diagonal_len_list.files)                          # 出错时查看
            x_parameters = diagonal_len_list['linear_model_x']
            y_parameters = diagonal_len_list['plot_y']
        else:
            # 不存在该文件报错
            print("================")
            print("不存在diagonal_len_list.npz")
            return False

    predictions = {}                                # 规定函数数据以字典形式存储
    regr = LinearRegression()                       # 创建实例
    regr.fit(x_parameters, y_parameters)            # 输入x、y轴数据，且进行线性回归
    if predict_value:                               # 依据x坐标计算函数值
        predictions['predicted_value'] = regr.predict(X=predict_value)
    predictions['intercept'] = regr.intercept_      # 截止点，f(0)
    predictions['coefficient'] = regr.coef_         # 斜率k

    # 保存线性回归结果数据到文件
    np.save(current_path + '/predictions_model.npy', predictions)

    if show:
        plt.scatter(x_parameters, y_parameters, color='blue')  # 散点图
        plt.plot(x_parameters, regr.predict(X=x_parameters), color='red', linewidth=4)  # 画出线性回归线
        # plt.xticks(())
        # plt.yticks(())
        plt.show()

    return predictions


def correct(row, line):
    """
    用于param_correction和make_predict_model过程第一步的位置修正

    Parameters
    ----------
    row
        目前所在柜桶的行，0开始，顺轴正向增加
    line
        目前所在柜桶的列，0开始，顺轴正向增加

    """
    # 1.1 指定药物编号的json数据
    params_correction_xyz = params_correction.get_ark_barrels(row, line)  # 指定药柜的修正参数
    # 1.2 柜桶相关信息
    ark_z_info = ark_barrels_coordinates.get_z()
    ark_y_info = ark_barrels_coordinates.get_y()

    # 1.3 x，z轴对准参数获取
    # x轴对基准柜桶二维码x方向中心
    camera_x, ark_barrels_x_center = \
        x_correct_coordinates(row, line, params_correction_xyz[0])
    # z轴对基准柜桶二维码z方向中心
    camera_z, z_qr_code = \
        z_correct_coordinates(row, line, ark_z_info, params_correction_xyz[2])

    # 1.4 x轴修正对齐，夹子中心对齐柜桶中心,z轴修正对齐，尖端底部与药板支撑面平齐
    # 同时进行节约时间
    go.xz(coordinate_now_x=camera_x,
          coordinate_target_x=ark_barrels_x_center,
          coordinate_now_z=camera_z,
          coordinate_target_z=z_qr_code)
    time.sleep(sleep_time)

    # 1.5 y轴修正，前进到 尖端 与 影像识别边 相距 5mm
    image_recognition_coordinate = y_correct(params_correction_xyz[1], 5)
    time.sleep(sleep_time)
    return


def param_correction(row, line):
    """
    实现指定柜桶的y坐标偏移量的获取并更新到对应的params_correction.json文件中

    Parameters
    ----------
    row
        目前所在柜桶的行，0开始，顺轴正向增加
    line
        目前所在柜桶的列，0开始，顺轴正向增加

    Returns
    -------
    """
    # 1、根据标准记录移动到指定柜桶的位置
    correct(row, line)
    # =========================================第一步完成=========================================

    # 2、拍照识别返回偏差值y_offset


    # =========================================第二步完成=========================================

    # 3、更新param_correction.json文件对应的柜桶数据中

    # params_correction.record_ark_barrels(row, line, [x_offset, 0, 0])
    # =========================================第三步完成=========================================

    return


def qr_code_collect():
    """
    二维码图像样本采集，采集一系列不同物距的图像样本

    Returns
    -------
    return
        picture_dir_path - 照片目录的绝对路径
    """
    # 获取目前y坐标
    origin_coordinates_y = current_coordinates.get('motor_y')

    video_qr = camera.Video(camera.DEVICE_NAME_QR)                      # 创建柜桶二维码图像实例
    video_qr.set_parm(focus_absolute=camera.FOCUS_ABSOLUTE_QR,          # 设置成像参数
                      exposure_absolute=camera.EXPOSURE_ABSOLUTE_QR)
    # 采样位置初始化
    init_y = -5         # 定义在current位置后退5mm的位置开始采样
    init_coordinates_y = origin_coordinates_y + init_y
    go.only_y(origin_coordinates_y, (init_coordinates_y - 1))       # 后退到初始点后1mm的位置
    go.only_y(0, 1)             # 前进到初始点，消除回程误差
    time.sleep(sleep_time)

    i = 5.0
    picture_dir_path = ''
    while i >= -5.0:
        # 移动y轴
        # 获取目前y坐标
        current_coordinates_y = current_coordinates.get('motor_y')
        # 根据原点计算目前y目标坐标
        target_coordinates_y = round(origin_coordinates_y - i, 8)
        print("目前y坐标：[%s]，目标点坐标：%s"
              % (current_coordinates_y, target_coordinates_y))
        go.only_y(current_coordinates_y, target_coordinates_y)  # Y轴运动

        dir_name = "qr_mode/"
        picture_name = dir_name + "QR_{0}".format(i)
        print(picture_name)
        img, picture_dir_path = video_qr.take_photo(picture_name=picture_name,
                           resolution=camera.RESOLUTION_QR)
        i = round(i - 0.1, 1)

    # 回到起始原点
    # 获取目前y坐标
    current_coordinates_y = current_coordinates.get('motor_y')
    # 根据原点计算目前y目标坐标
    target_coordinates_y = origin_coordinates_y
    print("目前y坐标：[%s]，目标点坐标：%s"
          % (current_coordinates_y, target_coordinates_y))
    go.only_y(current_coordinates_y, target_coordinates_y)  # Y轴运动

    return picture_dir_path


def linear_decode_all(picture_dir_path):
    """
    识别所有需要线性回归的二维码图片，线性回归需要的数据单独保存了一份文件。与返回的数据一致。
    diagonal_len_list.npz

    Parameters
    ----------
    picture_dir_path
        指定采样图像组的镜头拍照图片目录，需要加 "/qr_mode" 才进到图像组目录

    Returns
    -------
    Returns
        linear_model_x - x保存的是对角线距离
        plot_y - y保存的是物距偏差值
    """
    diagonal_len_list = []              # 识别距离结果存储列表
    linear_model_x = []                 # x保存的是对角线距离
    plot_y = []                         # y保存的是物距偏差值

    num = 5.0                           # 不同距离拍摄的二维码编号
    # 循环测量所有二维码的对角线
    while num >= -5.0:
        file_name = 'qr_mode/QR_{0}.jpg'.format(num)
        print(file_name)

        diagonal_len, data = qr_code.opposite_point_dis(file_name, dir_path=picture_dir_path + '/', strong=1)     # 识别
        if diagonal_len:
            diagonal_len_list.append([num, diagonal_len])               # 若识别成功了将结果添加到列表中
            linear_model_x.append([diagonal_len])
            plot_y.append(num)

        num = round(num - 0.1, 1)  # 步进为0.1，保留小数位避免极小值

    # 保存坐标到文件
    np.savez(current_path + '/diagonal_len_list', linear_model_x=linear_model_x, plot_y=plot_y)
    # 打印查看
    print("=====================")
    print("最终所有的对角线为")
    i = 0
    for j in diagonal_len_list:
        print(diagonal_len_list[i])
        i += 1

    return linear_model_x, plot_y


def make_predict_model(row, line):
    """
    建立预测模型的主函数

    Parameters
    ----------
    row
        目前所在柜桶的行，0开始，顺轴正向增加
    line
        目前所在柜桶的列，0开始，顺轴正向增加

    """
    # 1、根据标准记录移动到指定柜桶的位置
    # correct(row, line)

    # 2、移动采集图像
    # picture_dir_path = qr_code_collect()

    picture_dir_path = '/home/pi/Documents/yunxun/pywork143/image/picture/video2'
    # 3、分析图像样本获取数组列表数据
    # linear_decode_all(picture_dir_path)

    # 4、线性回归获取标准模型参数
    # linear_model_main(show=1)

    # Intercept value，截距： 105.11169626
    # coefficient，斜率： -0.06209825

    # Intercept value，截距： 110.25228396
    # coefficient，斜率： -0.0657483

    # 读取数据查看是否正常
    if debug:
        predictions = np.load(current_path + '/predictions_model.npy', allow_pickle=True).item()
        intercept = round(predictions['intercept'], 8)  # 截距
        coefficient = round(predictions['coefficient'][0], 8)  # 系数，斜率
        print("Intercept value，截距：", intercept)
        print("coefficient，斜率：", coefficient)

    return


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
    # =============== 线性回归数据存储测试 ==================
    # linear_model_main(show=1)
    # predictions = np.load('predictions_model.npy', allow_pickle=True).item()
    # intercept = round(predictions['intercept'], 8)                      # 截距
    # coefficient = round(predictions['coefficient'][0], 8)               # 系数，斜率
    # print("Intercept value ", intercept)
    # print("coefficient", coefficient)

    # print(result['intercept'])

    # ============== 小测试 ==============
    # predictions_test = {'intercept':1, 'coefficient':2}
    # np.save('predictions_model.npy', predictions_test)
    #
    # # predictions_get = np.load('predictions_model.npy', allow_pickle=True).item()
    # # print(predictions_get['intercept'])
    # predictions_get = np.load('predictions_model.npy', allow_pickle=True)
    # print(predictions_get['intercept'])

    i = 5.0
    while i >= -5.0:
        dir_name = "qr_mode/"
        picture_name = dir_name + "QR_{0}".format(i)
        print(picture_name)
        i = round(i - 0.1, 1)

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
