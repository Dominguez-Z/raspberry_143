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
# ############################ 常数值设定区域 ############################
current_path = os.path.dirname(__file__)        # 获取本文件的路径
picture_dir_path = current_path + "/picture"     # 加上目标文件的相对路径
camera = 'video0'                              # 指定摄像头对应的文件名
picture_camera_0_path = picture_dir_path + '/' + camera + '.jpg'           # 图片文件路径
# ########################################################################


# ############################### 函数说明 ###############################
# take_photo函数实现调用成功将拍照记录在/picture/目录下的对应文件名的jpg图片
# ########################################################################
def take_photo(picture_name=None):
    if os.path.exists(picture_dir_path):
        pass
    else:
        os.makedirs(picture_dir_path)
    # 设置照片名字
    if picture_name:
        picture_camera_path = picture_dir_path + '/' + picture_name + '.jpg'
    else:
        picture_camera_path = picture_camera_0_path
    dev_video_path = '/dev/' + camera
    os_popen_instruct = 'fswebcam -d '+ dev_video_path + ' --no-banner -r 1600x1200 -S 10 ' \
                        + picture_camera_path
    os.system(os_popen_instruct)

    return


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
    take_photo()
    time.sleep(0.5)
    # for i in range(101):
    #     number = i * 0.05
    #     for j in range(5):
    #         picture_name = "L_" + str("%.2f"%number) + "_" + str(j)
    #         print(picture_name)
    #         take_photo(picture_name)
    for i in range(101):
        number = i * 0.05
        for j in range(5):
            picture_name = "R_" + str("%.2f" % number) + "_" + str(j)
            print(picture_name)
            take_photo(picture_name)
            # time.sleep(0.5)
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
