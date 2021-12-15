#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  camera.py
#      Author:  钟东佐
#       Date        ||      describe
#   2021/7/214      ||  创建摄像头类，包括摄像头参数的设置，拍照，照片展示
#########################################################
import os
import cv2
import time
import wiringpi
import motor.go as go
import motor.y_drive as y
import JSON.current_coordinates as current_coordinates

# 测试记号
time_test = 0
v4l2_info_show = 0
cv2_imshow = 0
cv2_imshow2gray = 0  # 监测图像的时候可以选择灰度显示
cv2_imwrite = 1

# video0
DEVICE_NAME_BOTTLE = 'video0'
FOCUS_ABSOLUTE_BOTTLE = 190
EXPOSURE_ABSOLUTE_BOTTLE = 500
RESOLUTION_BOTTLE = [3264, 2448]

DEVICE_NAME_PLATE = 'video0'
FOCUS_ABSOLUTE_PLATE = 200
EXPOSURE_ABSOLUTE_PLATE = 200
RESOLUTION_PLATE = [3264, 2448]

WHITE_BALANCE_TEMPERATURE_0 = 4600

# video1
# ========二维码========
DEVICE_NAME_QR = 'video2'
FOCUS_ABSOLUTE_QR = 350
EXPOSURE_ABSOLUTE_QR = 350  # 曝光量,调整到二维码亮部黑色灰度95左右，暗部白的175左右，识别率较高
RESOLUTION_QR = [3264, 2448]
COEFFICIENT_QR = 38.53 * 1e-3  # 像素转mm的比例系数

# ==========柜桶===========
DEVICE_NAME_ARK = 'video2'
FOCUS_ABSOLUTE_ARK = 350
EXPOSURE_ABSOLUTE_ARK = 1000  # 曝光量
RESOLUTION_ARK = [3264, 2448]
# RESOLUTION_ARK = [640, 480]
COEFFICIENT_ARK = 37.8 * 1e-3  # 像素转mm的比例系数

# ============夹具=============
DEVICE_NAME_TONG = 'video2'
FOCUS_ABSOLUTE_TONG = 400
EXPOSURE_ABSOLUTE_TONG = 3000
RESOLUTION_TONG = [3264, 2448]
COEFFICIENT_TONG = 26.9 * 1e-3  # 像素转mm的比例系数

WHITE_BALANCE_TEMPERATURE_1 = 4600


class Video(object):
    """
    包括摄像头参数的设置，拍照，照片展示
    """

    def __init__(self, device_name: str):
        """
        初始化摄像头编号，硬件接口1-4，对应video0-3

        Parameters
        ----------
        device_name
            摄像头设备号，举例：video0
        """
        self.video = device_name  # 指定摄像头对应的设备名

        # ############################ 常数值设定区域 ############################
        self.current_path = os.path.dirname(__file__)  # 获取本文件的路径
        self.picture_dir_path = self.current_path + "/picture/" + device_name  # 加上目标文件的相对路径
        self.picture_path = self.picture_dir_path + '/' + device_name + '.jpg'  # 图片文件路径
        self.dev_video_path = '/dev/' + device_name  # linux下的设备号
        # ########################################################################

    def set_parm(self,
                 focus_absolute=None,
                 exposure_absolute=None,
                 white_balance_temperature=None):
        """
        设置摄像头参数

        Parameters
        ----------
        focus_absolute
            焦距，未指定时不变，给0时自动对焦。
            范围为：[0, 1023]
        exposure_absolute
            曝光绝对值,未指定不变，给0时，exposure_auto=0，为模式0。
            范围为：[50, 10000]
        white_balance_temperature
            色温，未指定不变，给0时为自动
            范围为：[2800, 6500]
        """
        diver_set_str = '-d' + self.dev_video_path
        print("============%s设置============" % self.video)
        # 设置色温
        if white_balance_temperature:
            os.system("v4l2-ctl --set-ctrl=white_balance_temperature_auto=0")
            os.system("v4l2-ctl --set-ctrl=white_balance_temperature=" + str(white_balance_temperature))
            print("色温%s" % white_balance_temperature)
        elif white_balance_temperature == 0:
            os.system("v4l2-ctl --set-ctrl=white_balance_temperature_auto=1")
            print("色温自动")
        else:
            pass

        # 设置曝光
        if exposure_absolute:
            print("曝光度为：%s" % exposure_absolute)
            # fps和曝光度都关闭自动
            os.system("v4l2-ctl " + diver_set_str + " --set-ctrl=exposure_auto=1")
            """
            0   ||  V4L2_EXPOSURE_AUTO              ||  Automatic exposure time, automatic iris aperture.
            1   ||  V4L2_EXPOSURE_MANUAL            ||  Manual exposure time, manual iris.
            2   ||  V4L2_EXPOSURE_SHUTTER_PRIORITY  || Manual exposure time, auto iris.
            3   ||  V4L2_EXPOSURE_APERTURE_PRIORITY || Auto exposure time, manual iris.
            """
            # 设置曝光度
            os.system("v4l2-ctl " + diver_set_str + " --set-ctrl=exposure_absolute=" + str(exposure_absolute))

            # exposure_auto_priority=0是锁定camera的fps，exposure_auto_priority=1是fps不固定，曝光设置优先。
            os.system("v4l2-ctl " + diver_set_str + " --set-ctrl=exposure_auto_priority=1")
        elif exposure_absolute == 0:
            print("曝光度自动调整")
            # fps和曝光度都开启自动
            os.system("v4l2-ctl " + diver_set_str + " --set-ctrl=exposure_auto=0")
            # 锁定camera的fps
            os.system("v4l2-ctl " + diver_set_str + " --set-ctrl=exposure_auto_priority=0")
        else:
            pass

        # 设置焦距
        if focus_absolute:
            # 关闭自动对焦
            os.system("v4l2-ctl " + diver_set_str + " --set-ctrl=focus_auto=0")
            os.system("v4l2-ctl " + diver_set_str + " --set-ctrl=focus_absolute=" + str(focus_absolute))
            print("焦距：%s" % focus_absolute)
        elif focus_absolute == 0:
            # 开启自动对焦
            os.system("v4l2-ctl " + diver_set_str + " --set-ctrl=focus_auto=1")
            print("自动对焦")
        # time.sleep(0.1)
        else:
            pass

        print("=============设置结束=============")

        return

    def take_photo(self, picture_name=None, resolution=None, cut_range=None, monitor=None):
        """
        实现将拍照记录在/picture目录下的对应设备名目录下的对应文件名的jpg图片

        Parameters
        ----------
        picture_name
            照片的名字,默认记录的是JPG图片，不需要添加后缀
        resolution
            照片的分辨率，默认为[1600, 1200]
            支持：  3264X2448 @ 15fps / 2592X1944@ 20fps /
                    2048X1536 @ 20fps / 1600X1200@ 20fps /
                    1280X960 @ 20fps / 1024X768@ 30fps /
                    800X600 @ 30fps / 640X480@ 30fps
        cut_range
            图片需要裁切的范围，[y1, y2, x1, x2]
        monitor
            监控是否开启，默认为关闭。置1为开启，开启监控后可以实时看到摄像头画面，按t进行拍照，按q退出监控。

        Returns
        -------
        return
            img - 图像
            picture_dir_path - 照片目录的绝对路径
        """
        # 判断是否有照片目录，没有将创建
        if os.path.exists(self.picture_dir_path):
            pass
        else:
            os.makedirs(self.picture_dir_path)

        # 设置照片名字
        if picture_name:
            picture_path = self.picture_dir_path + '/' + picture_name + '.jpg'
            picture_cut_path = self.picture_dir_path + '/' + picture_name + '_cut' + '.jpg'
        else:
            picture_path = self.picture_dir_path + '/' + self.video + '.jpg'
            picture_cut_path = self.picture_dir_path + '/' + self.video + '_cut' + '.jpg'
        # 设置分辨率
        if resolution:
            cv2_width = resolution[0]
            cv2_height = resolution[1]
        else:
            cv2_width = 1600
            cv2_height = 1200

        # # 旧方案采用fswebcam拍照，新方案使用opencv获取img，因此旧代码注释留存
        # # 设置分辨率
        # if resolution:
        #     resolution_str = str(resolution[0]) + "x" + str(resolution[1])
        # else:
        #     resolution_str = "1600x1200"
        #
        # os_popen_instruct = 'fswebcam -d ' + self.dev_video_path + ' --no-banner -r ' + resolution_str \
        #                     + ' -S 2 ' + picture_path
        # # os_popen_instruct = 'fswebcam -d ' + self.dev_video_path + ' --no-banner -r 3264x2448 -S 10 ' \
        # #                     + picture_camera_path
        # os.system(os_popen_instruct)

        # 时间节点
        t_1 = 0  # 排除time_test = 0，t_1没有被赋值后续用了导致奔溃
        if time_test:
            t_1 = wiringpi.micros()
            t_1 = wiringpi.micros()

        # cap = cv2.VideoCapture(self.dev_video_path)           # 创建一个video实例
        cap = cv2.VideoCapture()  # 创建一个video实例
        cap.open(self.dev_video_path)  # 打开后执行设置set才能正常生效
        if not cap.isOpened():  # 判断打开是否正常，不正常直接退出
            print("相机打开失败，已退出")
            return False, self.picture_dir_path
        # 设置参数
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))  # 设置4字符编码的编码器，图片压缩过，较小，拍照快些
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)  # 设置缓存大小
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, cv2_width)  # 设置宽
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cv2_height)  # 设置高

        # 显示拍照前v4l2的全部参数
        if v4l2_info_show:
            os.system("v4l2-ctl --all")

        # 时间节点
        t_2 = 0
        if time_test:
            t_2 = wiringpi.micros()
            print("cv2设置占用的时间是%s" % (t_2 - t_1))

        # 直接拍照部分
        if not monitor:
            # 获取图片
            ret, frame = cap.read()
            # 如果有切片指令，则进行切片
            if cut_range:
                img = frame[cut_range[0]:cut_range[1], cut_range[2]:cut_range[3]]
            else:
                img = frame

            # 时间节点
            t_3 = 0
            if time_test:
                t_3 = wiringpi.micros()
                print("cv2拍照占用的时间是%s" % (t_3 - t_2))

            # 保存照片到文件方便测试时获知信息
            if cv2_imwrite:
                cv2.imwrite(picture_path, frame)
                if cut_range:
                    cv2.imwrite(picture_cut_path, img)

            # 时间节点
            t_4 = 0
            if time_test:
                t_4 = wiringpi.micros()
                print("cv2存照片占用的时间是%s" % (t_4 - t_3))

            # 显示图像
            if cv2_imshow:
                cv2.namedWindow('original', cv2.WINDOW_NORMAL)
                cv2.imshow('original', frame)
                if cut_range:
                    cv2.namedWindow('cut', cv2.WINDOW_NORMAL)
                    cv2.imshow('cut', img)
                cv2.waitKey(0)
                cv2.destroyAllWindows()

        # 监控拍照部分
        else:
            cv2.namedWindow('img', cv2.WINDOW_NORMAL)
            while True:
                t_start = wiringpi.micros()
                ret, img = cap.read()
                t_end = wiringpi.micros()
                print("每一帧占用的时间是%s" % (t_end - t_start))
                # 可选择转换为灰度图显示
                if cv2_imshow2gray:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                cv2.imshow('img', img)
                k = cv2.waitKey(1) & 0xFF
                if k == ord('t'):
                    cv2.imwrite(picture_path, img)
                    print('图片保存完成')
                elif k == ord('q'):
                    break
            cv2.destroyAllWindows()

        # 释放掉摄像头
        cap.release()
        return img, self.picture_dir_path

    def show(self, picture_name=None):
        """
        实现窗口展示图片

        """
        # 设置照片名字
        if picture_name:
            picture_path = self.picture_dir_path + '/' + picture_name + '.jpg'
        else:
            picture_path = self.picture_path

        img = cv2.imread(picture_path)

        cv2.namedWindow(picture_name, cv2.WINDOW_NORMAL)
        cv2.imshow(picture_name, img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return


# 初始化设定
def setup():
    y_setup_return = y.setup()
    if not y_setup_return:
        print('Y轴初始化失败')

    return True


def qr_code_test():
    # 获取目前y坐标
    origin_coordinates_y = current_coordinates.get('motor_y')

    video_1 = Video("video1")
    video_1.set_parm(exposure_absolute=EXPOSURE_ABSOLUTE_QR,
                     focus_absolute=FOCUS_ABSOLUTE_QR)
    i = 0.0
    while i <= 3.5:
        # 移动y轴
        # 获取目前y坐标
        current_coordinates_y = current_coordinates.get('motor_y')
        # 根据原点计算目前y目标坐标
        target_coordinates_y = round(origin_coordinates_y - i, 8)
        print("目前y坐标：[%s]，目标点坐标：%s"
              % (current_coordinates_y, target_coordinates_y))
        go.only_y(current_coordinates_y, target_coordinates_y)  # Y轴运动

        picture_name = "test_QR_{0}".format(i)
        print(picture_name)
        video_1.take_photo(picture_name=picture_name,
                           resolution=RESOLUTION_QR)
        i = round(i + 0.1, 1)

    # 回到起始原点
    # 获取目前y坐标
    current_coordinates_y = current_coordinates.get('motor_y')
    # 根据原点计算目前y目标坐标
    target_coordinates_y = origin_coordinates_y
    print("目前y坐标：[%s]，目标点坐标：%s"
          % (current_coordinates_y, target_coordinates_y))
    go.only_y(current_coordinates_y, target_coordinates_y)  # Y轴运动

    return


# 循环部分
def main():
    # # =============video1-二维码y移动拍照===============
    # qr_code_test()
    # # =============测试结束===============

    # ===============video0-药板成像测试============
    video_plate = Video(DEVICE_NAME_PLATE)
    video_plate.set_parm(exposure_absolute=EXPOSURE_ABSOLUTE_PLATE,
                         focus_absolute=FOCUS_ABSOLUTE_PLATE)
    video_plate.take_photo(picture_name="test_PLATE",
                           resolution=RESOLUTION_PLATE,
                           monitor=1)
    # ================测试结束======================

    # ===============video1-QR测试============
    # video_1 = Video(DEVICE_NAME_QR)
    # video_1.set_parm(exposure_absolute=EXPOSURE_ABSOLUTE_QR,
    #                  focus_absolute=FOCUS_ABSOLUTE_QR)
    # video_1.take_photo(picture_name="test_QR",
    #                    resolution=RESOLUTION_QR,
    #                    monitor=1)
    # =============测试结束===============

    # video_1.set_parm(exposure_absolute=EXPOSURE_ABSOLUTE_ARK)
    # i = 0
    # while i <= 3.5:
    #     picture_name = "test_QR_{0}".format(i)
    #     print(picture_name)
    #     # video_1.take_photo(picture_name=picture_name,
    #     #                    resolution=RESOLUTION_ARK, )
    #     i = round(i+0.1, 1)
    # video_1.take_photo(picture_name="test_QR",
    #                    resolution=RESOLUTION_ARK,)
    # monitor=1)

    # video_bottle = Video("video0")
    # video_bottle.set_parm(focus_absolute=FOCUS_ABSOLUTE_BOTTLE,
    #                       exposure_absolute=EXPOSURE_ABSOLUTE_BOTTLE)
    # video_bottle.take_photo(picture_name="test_light",
    #                         resolution=RESOLUTION_BOTTLE,
    #                         monitor=1)
    # video_1.take_photo()
    # i = 340
    # while i <= 360:
    #     video_1.set_parm(focus_absolute=i)
    #     video_1.take_photo(str(i), RESOLUTION_TONG)
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
    y.destroy()
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
