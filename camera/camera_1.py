#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  camera_1.py
#      Author:  钟东佐
#        Date:  2020/5/26
#    describe:  1号摄像头的控制
#########################################################
import os
import cv2
# ############################ 常数值设定区域 ############################
current_path = os.path.dirname(__file__)        # 获取本文件的路径
picture_dir_path = current_path + "/picture"     # 加上目标文件的相对路径
camera1 = 'video1'                              # 指定摄像头对应的文件名
picture_camera_1_path = picture_dir_path + '/' + camera1 + '.jpg'           # 图片文件路径
# ########################################################################


# ############################### 函数说明 ###############################
# take_photo函数实现调用成功将拍照记录在/picture/目录下的对应文件名的jpg图片
# ########################################################################
def take_photo():
    if os.path.exists(picture_dir_path):
        pass
    else:
        os.makedirs(picture_dir_path)

    dev_video_path = '/dev/' + camera1
    os_popen_instruct = 'fswebcam -d '+ dev_video_path + ' --no-banner -r 320x240 -S 10 ' \
                        + picture_camera_1_path
    os.system(os_popen_instruct)

    return


# ############################### 函数说明 ###############################
# show函数实现窗口展示图片
# ########################################################################
def show():
    video0_img = cv2.imread(picture_camera_1_path)

    cv2.namedWindow('video1', cv2.WINDOW_NORMAL)
    cv2.imshow('video1', video0_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return

# 初始化设定
def setup():
    return True


# 循环部分
def main():
    take_photo()
    show()

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
