#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  camera_0.py
#      Author:  钟东佐
#        Date:  2020/5/26
#    describe:  0号摄像头的控制
#########################################################
import os
import cv2
import time
import wiringpi
# ############################ 常数值设定区域 ############################
current_path = os.path.dirname(__file__)                    # 获取本文件的路径
picture_dir_path = current_path + "/picture/camera0"        # 加上目标文件的相对路径
camera = 'video0'                                           # 指定摄像头对应的文件名
picture_camera_0_path = picture_dir_path + '/' + camera + '.jpg'           # 图片文件路径
# 测试记号
time_test = 1
v4l2_info_show = 1
cv2_imshow = 1
cv2_imwrite = 1
# 参数

FOCUS_ABSOLUTE_BOTTLE = 190
WHITE_BALANCE_TEMPERATURE_BOTTLE = 6500

WHITE_BALANCE_TEMPERATURE_DEFAULT = 4600
# ########################################################################


def take_photo(picture_name=None,
               focus_absolute=None,
               cut_range=None,
               white_balance_temperature=None):
    """
    实现将拍照记录在/picture/camera0目录下的对应文件名的jpg图片

    Parameters
    ----------
    picture_name
        照片的名字,默认记录的是JPG图片，不需要添加后缀
    cut_range
        图片需要裁切的范围，[y1, y2, x1, x2]
    focus_absolute
        焦距，不给定时自动对焦。
    white_balance_temperature
        色温，不给定时默认4600,[2800, 6500]

    Returns
    -------
    return
        img - 图像
        picture_dir_path - 照片目录的绝对路径

    """
    if time_test:
        t1 = wiringpi.micros()
        t1 = wiringpi.micros()

    if os.path.exists(picture_dir_path):
        pass
    else:
        os.makedirs(picture_dir_path)

    # 设置色温
    # 关闭自动
    # os.system("v4l2-ctl --set-ctrl=white_balance_temperature_auto=1")
    if white_balance_temperature:
        os.system("v4l2-ctl --set-ctrl=white_balance_temperature_auto=0")
        os.system("v4l2-ctl --set-ctrl=white_balance_temperature=" + str(white_balance_temperature))
        print("设置了色温")
    else:
        os.system("v4l2-ctl --set-ctrl=white_balance_temperature_auto=1")
        print("设置了色温自动")

    # 设置曝光
    os.system("v4l2-ctl --set-ctrl=exposure_auto=1")
    """
    0   ||  V4L2_EXPOSURE_AUTO              ||  Automatic exposure time, automatic iris aperture.
    1   ||  V4L2_EXPOSURE_MANUAL            ||  Manual exposure time, manual iris.
    2   ||  V4L2_EXPOSURE_SHUTTER_PRIORITY  || Manual exposure time, auto iris.
    3   ||  V4L2_EXPOSURE_APERTURE_PRIORITY || Auto exposure time, manual iris.
    """
    os.system("v4l2-ctl --set-ctrl=exposure_absolute=3000")
    # os.system("v4l2-ctl --set-ctrl=exposure_absolute=500")
    os.system("v4l2-ctl --set-ctrl=exposure_auto_priority=1")

    # 设置焦距
    if focus_absolute:
        # 关闭自动对焦
        os.system("v4l2-ctl --set-ctrl=focus_auto=0")
        os.system("v4l2-ctl --set-ctrl=focus_absolute=" + str(focus_absolute))
        print("设置了焦距")
    else:
        # 开启自动对焦
        os.system("v4l2-ctl --set-ctrl=focus_auto=1")
        print("自动对焦")
    # time.sleep(0.5)

    # 设置v4l2的图像格式
    # os.system("v4l2-ctl --set-fmt-video=width=3264,height=2448,pixelformat=MJPG")
    # os.system("v4l2-ctl --set-fmt-video=width=3264,height=2448,pixelformat=YUYV")
    # os.system("v4l2-ctl --all")

    # 设置照片名字
    if picture_name:
        picture_camera_path = picture_dir_path + '/' + picture_name + '.jpg'
    else:
        picture_camera_path = picture_camera_0_path
    dev_video_path = '/dev/' + camera
    # os_popen_instruct = 'fswebcam -d ' + dev_video_path + ' --no-banner -r 1600x1200 -S 2 ' \
    #                     + picture_camera_path
    os_popen_instruct = 'fswebcam -d ' + dev_video_path + ' --no-banner -r 3264x2448 -S 1 ' \
                        + picture_camera_path
    # os.system("v4l2-ctl --all")

    if time_test:
        t2 = wiringpi.micros()
        print("设置拍照参数占用的时间是%s" % (t2 - t1))

    # os.system(os_popen_instruct)
    # return picture_camera_path

    cap = cv2.VideoCapture(0)
    # ret, frame = cap.read()
    # cv2.imshow('medicine', frame)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    cap.open(0)
    if not cap.isOpened():
        print("相机打开失败，已退出")
        return False, picture_dir_path
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3264)     # set Width
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2448)    # set Height
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3264)  # set Width
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2448)  # set Height
    # cap.set(cv2.CAP_PROP_FPS, 5)               # 帧率，帧 / 秒
    # cap.set(cv2.CAP_PROP_BUFFERSIZE, 5)
    if v4l2_info_show:
        os.system("v4l2-ctl --all")

    if time_test:
        t_s = wiringpi.micros()
        print("cv2设置占用的时间是%s" % (t_s - t2))

    # 获取图片且不要第一帧
    cap.read()
    ret, frame = cap.read()
    # 如果有切片指令，则进行切片
    if cut_range:
        img = frame[cut_range[0]:cut_range[1], cut_range[2]:cut_range[3]]
    else:
        img = frame

    if time_test:
        t3 = wiringpi.micros()
        print("cv2拍照占用的时间是%s" % (t3 - t_s))

    if cv2_imshow:
        cv2.imshow('medicine', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    if time_test:
        t4 = wiringpi.micros()

    if cv2_imwrite:
        cv2.imwrite(picture_camera_path, frame)
        cv2.imwrite(picture_dir_path + "/img_cut.jpg", img)

    if time_test:
        t5 = wiringpi.micros()
        print("cv2存照片占用的时间是%s" % (t5 - t4))

    # while True:
    #     t_s = wiringpi.micros()
    #
    #     ret, frame = cap.read()
    #
    #     t3 = wiringpi.micros()
    #     print("cv2拍照占用的时间是%s" % (t3 - t_s))
    #
    #     cv2.imshow('medicine', frame)
    #     if cv2.waitKey(1) == ord('t'):
    #         t4 = wiringpi.micros()
    #         cv2.imwrite(picture_camera_path, frame)
    #         t5 = wiringpi.micros()
    #         print("cv2存照片占用的时间是%s" % (t5 - t4))
    #
    #         cv2.destroyAllWindows()
    #         break

    return img, picture_dir_path


# ############################### 函数说明 ###############################
# show函数实现窗口展示图片
# ########################################################################
def show(picture_name=None):
    # 设置照片名字
    if picture_name:
        picture_camera_path = picture_dir_path + '/' + picture_name + '.jpg'
    else:
        picture_name = camera
        picture_camera_path = picture_camera_0_path
    video0_img = cv2.imread(picture_camera_path)

    cv2.namedWindow(picture_name, cv2.WINDOW_NORMAL)
    cv2.imshow(picture_name, video0_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return


# 初始化设定
def setup():
    return True


# 循环部分
def main():
    take_photo(picture_name="test1")
    time.sleep(0.5)
    # for i in range(101):
    #     number = i * 0.05
    #     for j in range(5):
    #         picture_name = "L_" + str("%.2f"%number) + "_" + str(j)
    #         print(picture_name)
    #         take_photo(picture_name)
    # for i in range(101):
    #     number = i * 0.05
    #     for j in range(5):
    #         picture_name = "R_" + str("%.2f" % number) + "_" + str(j)
    #         print(picture_name)
    #         take_photo(picture_name)
    #         time.sleep(0.5)
    # take_photo("1")
    # show("1")

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
