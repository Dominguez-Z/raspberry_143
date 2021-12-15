# -*- coding:utf-8 -*-
import zxing
import re
import numpy as np
import math
import matplotlib.pyplot as plt
from PIL import Image, ImageEnhance
import pandas as pd
from sklearn.linear_model import LinearRegression


def linear_model_main(X_parameters, Y_parameters, predict_value=None):
    regr = LinearRegression()
    regr.fit(X_parameters, Y_parameters)
    if predict_value:
        predict_outcome = regr.predict(predict_value)
    predictions = {}
    predictions['intercept'] = regr.intercept_
    predictions['coefficient'] = regr.coef_
    if predict_value:
        predictions['predicted_value'] = predict_outcome

    return predictions


def show_linear_line(X_parameters, Y_parameters):
    regr = LinearRegression()
    regr.fit(X_parameters, Y_parameters)
    plt.scatter(X_parameters, Y_parameters, color='blue')
    plt.plot(X_parameters, regr.predict(X_parameters), color='red', linewidth=4)
    # plt.xticks(())
    # plt.yticks(())
    plt.show()


def qr_code_read_all():
    reader = zxing.BarCodeReader()
    diagonal_len_list = []

    num = 0.0
    # 循环测量左右二维码的对角线
    while num <= 3.5:
        filename = 'test_QR_{0}.jpg'.format(num)
        print(filename)
        barcode = reader.decode(filename)
        # 二维码识别成功了才进行提取距离
        if barcode.type:
            code = str(barcode)
            print("======code======")
            print(code)
            # print(barcode.type)

            matchObj = re.match( r'(.*) \'TEXT\', (.*)', code, re.M|re.I)
            print("======matchObj======")
            print(matchObj)

            set = matchObj.group(2)
            print("======set======")
            print(set)
            set = set.replace('\'TEXT\', ','').replace('), (',',').replace(')])','').replace('[(','').replace(' ','')
            print(set)
            set = set.split(',')
            print(set)
            long = []
            for i in range(len(set)):
                data = float(set[i])
                # data = int(data)
                long.append(data)
            print(long)
            # [2318, 1941, 1126, 1960, 1116, 789, 2162, 912]
            # 计算二维码1号和3号位置探测图形的像素距离
            p1 = np.array([long[0], long[1]])
            p2 = np.array([long[4], long[5]])
            p3 = p2 - p1
            diagonal_len = round(math.hypot(p3[0], p3[1]), 8)
            print("p3[0]：%s，p3[1]：%s" % (p3[0], p3[1]))
            print("%s二维码1号和3号位置探测图形的像素距离：%s" % (num, diagonal_len))

            diagonal_len_list.append([num, diagonal_len])
        # # 识别不到的默认为0
        # else:
        #     diagonal_len_list.append([num, 0])
        num = round(num+0.1, 1)             # 步进为0.1，保留小数位避免极小值

    print("=====================")
    print("最终所有的对角线为")
    # 画图的参数
    plot_x = []
    linear_model_x = []
    plot_y = []

    i = 0
    for j in diagonal_len_list:
        print(diagonal_len_list[i])
        plot_x.append(diagonal_len_list[i][1])
        linear_model = [diagonal_len_list[i][1]]
        linear_model_x.append(linear_model)
        plot_y.append(diagonal_len_list[i][0])
        i += 1

    # 画图
    # fig = plt.figure()
    # ax = fig.add_subplot(1,1,1)
    # ax.plot(plot_x,plot_y)
    # plt.show()


    # print(plot_x)
    # print(linear_model_x)
    # print(plot_y)
    return linear_model_x, plot_y


def qr_code_read(num=0.0):
    """
    单张二维码识别

    """
    # filename = 'test_QR_{0}.jpg'.format(num)
    filename = '{0}.jpg'.format(num)
    print(filename)
    reader = zxing.BarCodeReader()

    barcode = reader.decode(filename)
    print(barcode)
    # 二维码识别成功了才进行提取距离
    if barcode.type:
        code = str(barcode)
        print("======code======")
        print(code)
        # print(barcode.type)

        matchObj = re.match( r'(.*) \'TEXT\', (.*)', code, re.M|re.I)
        print("======matchObj======")
        print(matchObj)

        set = matchObj.group(2)
        print("======set======")
        print(set)
        set = set.replace('\'TEXT\', ','').replace('), (',',').replace(')])','').replace('[(','').replace(' ','')
        print(set)
        set = set.split(',')
        print(set)
        long = []
        for i in range(len(set)):
            data = float(set[i])
            # data = int(data)
            long.append(data)
        print(long)
        # [2318, 1941, 1126, 1960, 1116, 789, 2162, 912]
        # 计算二维码1号和3号位置探测图形的像素距离
        p1 = np.array([long[0], long[1]])
        p2 = np.array([long[4], long[5]])
        p3 = p2 - p1
        diagonal_len = round(math.hypot(p3[0], p3[1]), 8)
        print("p3[0]：%s，p3[1]：%s" % (p3[0], p3[1]))
        print("%s二维码1号和3号位置探测图形的像素距离：%s" % (filename, diagonal_len))

    # 识别不到
    else:
        print("================")
        print("识别不到二维码")

    return


def contrast_enhance(img_name):
    img = Image.open(img_name + '.jpg')
    # img.show()

    con_enh = ImageEnhance.Contrast(img)
    contrast = 2.0
    img_contrasted = con_enh.enhance(contrast)
    # img_contrasted.show()
    img_contrasted.save(img_name + '_enhed.jpg')
    return img_contrasted


# ==========单张二维码识别==========
contrast_enhance('12-1')         # 先增强对比度
qr_code_read('12-1_enhed')       # 再识别增强后的图片


# # ===========线性回归=============
# linear_model_x, plot_y = qr_code_read_all()
# result = linear_model_main(linear_model_x, plot_y)
# print("Intercept value ", result['intercept'])
# print("coefficient", result['coefficient'])
#
# show_linear_line(linear_model_x, plot_y)


# 0.0653106922933383
# 0.0   1677.43153735
# 0.1   1676.21008528
# 0.2   1673.72593336
# 0.3   1672.99865511
# 0.4   1671.07025959
# 3.5   1623.84458924
