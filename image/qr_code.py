#!/usr/bin/env python 
# -*- coding:utf-8 -*-
"""
二维码的创建和识别
"""
#########################################################
#   File name:  qr_code.py
#      Author:  钟东佐
#        Date:  2021/9/22
#       Date        ||      describe
#   2021/9/22       ||  新建二维码的生成函数make_qr,参考 www.jianshu.com/p/c0073c6aa544
#   2021/9/23       ||  加入二维码图片目录 qrcode 的管理
#   2021/9/24       ||  新建二维码识别函数 qr_code_read，
#########################################################
import qrcode
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageEnhance
import os
import zxing
import re
import numpy as np
import math
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import LinearRegression
import scipy

# ############################ 常数值设定区域 ############################
current_path = os.path.dirname(__file__)                        # 获取本文件的路径
qrcode_dir_path = current_path + "/qrcode/"                     # 加上目标文件的相对路径

# ########################################################################


def make_qr(data, name, logo=None, text=None):
    """
    生成二维码图片

    Parameters
    ----------
    data
        二维码包含的信息字符串
    name
        保存的文件名字，需要指定后缀，在 qrcode 目录下
    logo
        二维码中间需要添加的logo图片，默认不添加，
    text
        二维码下方增加空白区域添加字符串信息，默认不添加，置1为添加二维码包含的内容

    """
    # 生成二维码图片
    qrcode.QRCode()
    qr = qrcode.QRCode(
        version=1,                                          # 生成二维码尺寸的大小 1-40 格子 1:21*21（21+(n-1)*4）
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # L:7% M:15% Q:25% H:30%
        box_size=10,                                        # 每个格子的像素大小
        border=1,                                           # 白色边框的格子数量
    )
    qr.add_data(data)                                        # 添加二维码包含的信息
    qr.make(fit=True)                                       # 将信息载入二维码中。fit=True保证数据不会溢出
    img_qrcode = qr.make_image()                                   # 生成二维码图像

    # 加中间logo图片
    if logo:
        icon = Image.open("logo.png")
        img_w, img_h = img_qrcode.size
        factor = 4
        size_w = int(img_w / factor)
        size_h = int(img_h / factor)
        icon_w, icon_h = icon.size
        if icon_w > size_w:
            icon_w = size_w
        if icon_h > size_h:
            icon_h = size_h
        icon = icon.resize((icon_w, icon_h), Image.ANTIALIAS)
        w = int((img_w - icon_w) / 2)
        h = int((img_h - icon_h) / 2)
        img_qrcode.paste(icon, (w, h), icon)
        # print(str)

    # 保存二维码图片
    # 判断是否有照片目录，没有将创建
    if os.path.exists(qrcode_dir_path):
        pass
    else:
        os.makedirs(qrcode_dir_path)

    # 添加下方文字信息并保存图片
    if text == 1:
        background_path = qrcode_dir_path + "background.jpg"
        # 判断是否有底图，没有新建一张底图
        if os.path.exists(background_path):
            img_background = Image.open(background_path)
        else:
            # 创建底图，RGB模式，230*230，全白
            img_background = Image.new('RGB', (230, 230 + 80), (255, 255, 255))
            # img.show()
            img_background.save("background.jpg")

        img_background.paste(img_qrcode, (0, 0))            # 贴图,将二维码放在底图上
        # 添加文字
        qrcode_text_path = qrcode_dir_path + "编号" + name
        draw = ImageDraw.Draw(img_background)
        font = ImageFont.truetype("SIMHEI.TTF", 30)         # 设置字体，黑体
        # linux中文字体缺失，参考https://blog.csdn.net/bona020/article/details/51340704
        draw.text((20, 230), "编号", (1, 1, 1), font=font)  # 把字添加到图片上
        draw.text((20, 270), data, (1, 1, 1), font=font)
        img_background.save(qrcode_text_path)

    # 不需要添加文字的保存
    else:
        qrcode_path = qrcode_dir_path + name            # 组成图片路径
        img_qrcode.save(qrcode_path)

    return


def calculate_dis(barcode):
    """
    计算1和3号定位点的像素距离并返回

    Parameters
    ----------
    barcode
        BarCodeReader.decode解码获取的信息

    Returns
    -------
    Returns
        opposite_dis - 计算结果
    """
    point_1 = barcode.points[0]
    point_3 = barcode.points[2]

    # 计算二维码1号和3号位置探测图形的像素距离
    p1 = np.array([point_1[0], point_1[1]])
    p2 = np.array([point_3[0], point_3[1]])
    p3 = p2 - p1
    opposite_dis = round(math.hypot(p3[0], p3[1]), 8)  # 计算距离，保留8位小数
    print("p3[0]：%s，p3[1]：%s" % (p3[0], p3[1]))
    return opposite_dis


def opposite_point_dis(file_name, dir_path=None, strong=None):
    """
    识别二维码，返回1和3号定位点的像素距离,识别失败返回False

    Parameters
    ----------
    file_name
        需要识别的图片文件名字，默认图片在qrcode目录下
    dir_path
        二维码图片所在的目录，不指定时默认本文件目录下的/qrcode/
    strong
        置1开启强识别模式，识别失败自动增强对比度再识别，增强2次

    Returns
    -------
    Returns
        point_dis - 1和3号定位点的像素距离
        data - 二维码内容，给予判断是否正常识别

    """
    # 判断是否有指定二维码图片目录
    if dir_path:
        code_dir_path = dir_path
    else:
        code_dir_path = qrcode_dir_path

    qrcode_path = code_dir_path + file_name         # 组成图片的绝对路径
    reader = zxing.BarCodeReader()                  # 创建实例
    barcode = reader.decode(qrcode_path)            # 解码
    print(barcode)

    # 二维码识别成功了才进行提取距离
    # 解码成功 barcode 会有值，否则为空
    if barcode:
        data = barcode.parsed
        # 计算二维码1号和3号位置探测图形的像素距离
        opposite_dis = calculate_dis(barcode)
        print("%s二维码1号和3号位置探测图形的像素距离：%s" % (file_name, opposite_dis))
        return opposite_dis, data

    else:
        # 有指定进入强识别模式
        if strong:
            contrast_list = [3.0, 8.0]
            count = 0
            while count < 2:
                # 对比度增强
                img = Image.open(qrcode_path)
                # img.show()
                con_enh = ImageEnhance.Contrast(img)            # 根据原图创建实例
                contrast = contrast_list[count]                 # 设定增强的级别
                img_contrasted = con_enh.enhance(contrast)      # 执行增强
                print("第 %s 次增强二维码图片对比度" % (count+1))
                # img_contrasted.show()
                # 在原有的名字上加_enhed
                qrcode_enhed_path = qrcode_path.replace(".jpg", "", 1) + '_enhed{0}.jpg'.format(count)
                img_contrasted.save(qrcode_enhed_path)          # 保存图片
                count += 1                                      # 增加一次增强次数

                # 再次识别二维码内容
                barcode = reader.decode(qrcode_enhed_path)      # 解码
                print(barcode)
                # 解码成功 type 会有值，否则为空
                if barcode:
                    data = barcode.parsed
                    # 计算二维码1号和3号位置探测图形的像素距离
                    opposite_dis = calculate_dis(barcode)
                    print("%s二维码1号和3号位置探测图形的像素距离：%s" % (file_name, opposite_dis))
                    return opposite_dis, data

            # 增强后仍然识别不到
            print("================")
            print("识别不到二维码")
            return False, False

        # 未指定进入强识别直接退出
        else:
            print("================")
            print("识别不到二维码")
            return False, False


def linear_decode_all():
    """
    识别所有需要线性回归的二维码图片，线性回归需要的数据单独保存了一份文件。与返回的数据一致。
    diagonal_len_list.npz

    Returns
    -------
    Returns
        linear_model_x - x保存的是对角线距离
        plot_y - y保存的是物距偏差值

    """
    diagonal_len_list = []              # 识别距离结果存储列表
    linear_model_x = []                 # x保存的是对角线距离
    plot_y = []                         # y保存的是物距偏差值

    num = 0.0                           # 不同距离拍摄的二维码编号
    # 循环测量所有二维码的对角线
    while num <= 3.5:
        file_name = 'linear/test_QR_{0}.jpg'.format(num)
        print(file_name)

        diagonal_len, data = opposite_point_dis(file_name,strong=1)     # 识别
        if diagonal_len:
            diagonal_len_list.append([num, diagonal_len])               # 若识别成功了将结果添加到列表中
            linear_model_x.append([diagonal_len])
            plot_y.append(num)

        num = round(num + 0.1, 1)  # 步进为0.1，保留小数位避免极小值

    # 保存坐标到文件
    np.savez('diagonal_len_list', linear_model_x=linear_model_x, plot_y=plot_y)
    # 打印查看
    print("=====================")
    print("最终所有的对角线为")
    i = 0
    for j in diagonal_len_list:
        print(diagonal_len_list[i])
        i += 1

    return linear_model_x, plot_y


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
        if os.path.exists('diagonal_len_list.npz'):
            diagonal_len_list = np.load('diagonal_len_list.npz')
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
    np.save('predictions_model.npy', predictions)

    if show:
        plt.scatter(x_parameters, y_parameters, color='blue')  # 散点图
        plt.plot(x_parameters, regr.predict(X=x_parameters), color='red', linewidth=4)  # 画出线性回归线
        # plt.xticks(())
        # plt.yticks(())
        plt.show()

    return predictions


def setup():
    """
    初始化设定
    """

    return True


def main():
    """
    主函数
    """
    # # ============= 多张二维码识别 ===============
    # # linear_model_x, plot_y = linear_decode_all()
    # diagonal_len_list = np.load('diagonal_len_list.npz')
    # # print(diagonal_len_list.files)
    # # # print(diagonal_len_list['arr_0'])
    # result = linear_model_main(diagonal_len_list['linear_model_x'], diagonal_len_list['plot_y'], show=1)
    # # show_linear_line(linear_model_x, plot_y)

    # linear_model_main(show=1)
    # result = np.load('predictions_model.npy')
    # print(result.files)
    # print("Intercept value ", result['predictions']['intercept'])
    # print("coefficient", result['predictions']['coefficient'])

    # print("predicted_value", round(result['predicted_value'][0], 8))

    # # ============= 单张二维码识别 ===============
    # num = 9999999999
    # qrcode_data = str(num)
    #
    # # qrcode_name = qrcode_data + ".jpg"
    # # qrcode_name = "编号" + qrcode_data + ".jpg"
    qrcode_name = "url.png"
    #
    # # make_qr(data=qrcode_data, name=qrcode_name, text=1)
    opposite_dis, data = opposite_point_dis(file_name=qrcode_name, strong=1)
    print(type(data), data)

    # # ============= 单张二维码生成 ===============
    # num = 1111111111
    # time = 1
    # while time <= 9:
    #     number = num * time
    #     qrcode_data = str(number)
    #     qrcode_name = qrcode_data + ".jpg"
    #     make_qr(data=qrcode_data, name=qrcode_name, text=1)
    #     time += 1

    return


def destroy():
    """
    结束释放
    """
    return


if __name__ == '__main__':  # 程序从这开始
    """
    如果该程序为主程序，程序在此开始运行，若不是不运行，该文件只做函数定义
    """
    # 初始化
    setup_return = setup()
    if setup_return:
        print('始化成功')

    try:
        main()
    except KeyboardInterrupt:  # 当按下 'Ctrl+C', 子函数 destroy()将会运行，用于停止退出
        print("程序已停止退出...")
        destroy()

