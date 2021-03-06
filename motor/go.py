#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  go.py
#      Author:  钟东佐
#        Date:  2020/4/23
#    describe:  XYZ控制的底层代码封装，调用运动结束会更新坐标到JSON/constant_coordinates.json中
#########################################################
import time
import os
import json
import motor.y_drive as y
import motor.x_drive as x
import motor.z_drive as z
import motor.y1_drive as y1
import motor.x1_drive as x1
from JSON import current_coordinates
import JSON.coordinate_converter as coordinate_converter
import JSON.constant_coordinates as constant_coordinates
import JSON.ark_barrels_coordinates as ark_barrels_coordinates
import threading

# ############################ 常数值设定区域 ############################
current_path = os.path.dirname(__file__)            # 获取本文件的路径
constant_coordinates_file_path = current_path + "/../JSON/constant_coordinates.json"   # 加上目标文件的相对路径
# 各轴的范围
X_RANGE = [63.1, 1120.1]
Y_RANGE = [64.8, 199]
Z_RANGE = [15.3, 863.3]
X1_RANGE = [29, 69]
Y1_RANGE = [-121, 0]

# 记录坐标的小数位数
RECORD_DECIMALS = 8
# ########################################################################
# 创建一个线程锁，用于同时调用不同的轴时，更新坐标读写文件的时候产生冲突
threads_lock = threading.Lock()

def xz_move_y_safe():
    """
    调整y轴位置，保证在xz面运动过程中，主体部位不会碰撞柜桶。

    """
    # 推杆y方向前端坐标
    y_now = coordinate_converter.body_push_rod("the_front")
    # 安全位置为柜桶影像边后的一定位置
    y_target = constant_coordinates.get("xz_move_y_safe")
    only_y(y_now, y_target)
    return


def xz(coordinate_now_x, coordinate_target_x,
       coordinate_now_z, coordinate_target_z,
       rpm_max_x=450, rpm_max_z=450):
    """
    创建线程分别控制x、z轴运动，实现时间上同时启动。
    
    Parameters
    ----------
    coordinate_now_x
        当前x坐标
    coordinate_target_x
        目标x坐标
    coordinate_now_z
        当前z坐标
    coordinate_target_z
        目标z坐标
    rpm_max_x
        x轴运动最高转速设定，未指定按照默认
    rpm_max_z
        z轴运动最高转速设定，未指定按照默认
    """
    # xz平面运动前提是y方向不会碰撞
    xz_move_y_safe()

    # 创建x、z轴子线程
    threads = []
    t1 = threading.Thread(target=only_x, args=(coordinate_now_x, coordinate_target_x, rpm_max_x,))
    threads.append(t1)
    t2 = threading.Thread(target=only_z, args=(coordinate_now_z, coordinate_target_z, rpm_max_z,))
    threads.append(t2)
    # 将所有子线程开始
    for t in threads:
        t.setDaemon(True)
        t.start()
    # 打开子线程的阻塞保证所有子线程都运行完了，主线程才继续
    for t in threads:
        t.join()
        # print("threads : %s.time is: %s" % (t, ctime()))
    print('go_xz_success')
    return


def only_y(coordinate_now, coordinate_target, rpm_max=None):
    """
    接收y轴当前坐标和目标坐标,计算运动距离，指定控制，并更新坐标位置
    y轴运动最高转速可以指定

    Parameters
    ----------
    coordinate_now
        关注点当前坐标
    coordinate_target
        关注点目标坐标
    rpm_max
        运动最高转速设定，未指定按照默认

    """
    current_coordinates_y = current_coordinates.get('motor_y')  # 获取目前主体的坐标
    # 通过现有坐标和目的坐标计算需要走的距离，包含正负
    y_distance = coordinate_target - coordinate_now
    y_target = round(current_coordinates_y + y_distance, 1)        # 计算目标y轴的坐标,round避免往返运算的极小数
    # 判断目标y轴的坐标是否在允许范围内
    if Y_RANGE[0] <= y_target <= Y_RANGE[1]:
        print("86:目前y坐标：%s,位移量：%s" % (coordinate_now, y_distance))
        step_num, unit_step = y.move(y_distance, rpm_max)

        # 更新Y轴坐标
        y_distance_mm = round(step_num * unit_step, RECORD_DECIMALS)            # 计算出实际位移量mm
        current_coordinates_y += y_distance_mm                                  # 更新Y轴现有位置
        current_coordinates_y = round(current_coordinates_y, RECORD_DECIMALS)   # 限定小数点后8位
        # 线程加锁
        threads_lock.acquire()
        current_coordinates.record('motor_y', current_coordinates_y)            # 执行更新记录
        # 线程解锁
        threads_lock.release()
        print("96:更新后y坐标：%s" % current_coordinates_y)
    else:
        print("98:y轴运动将超出安全范围[%s, %s]，禁止此次运动" % (Y_RANGE[0], Y_RANGE[1]))
    return


def only_x(coordinate_now, coordinate_target, rpm_max=None):
    """
    接收x轴当前坐标和目标坐标,计算运动距离，指定控制，并更新坐标位置
    x轴运动最高转速可以指定

    Parameters
    ----------
    coordinate_now
        关注点当前坐标
    coordinate_target
        关注点目标坐标
    rpm_max
        运动最高转速设定，未指定按照默认

    """
    current_coordinates_x = current_coordinates.get('motor_x')              # 获取目前主体的坐标
    # 通过现有坐标和目的坐标计算需要走的距离，包含正负
    x_distance = coordinate_target - coordinate_now
    x_target = round(current_coordinates_x + x_distance, 1)               # 计算目标x轴的坐标,round避免往返运算的极小数
    # 判断目标x轴的坐标是否在允许范围内
    if X_RANGE[0] <= x_target <= X_RANGE[1]:
        print("110:目前x坐标：%s,位移量：%s" % (coordinate_now, x_distance))
        # 调用运动程序
        step_num, unit_step = x.move(x_distance, rpm_max)

        # 更新X轴坐标
        x_distance_mm = round(step_num * unit_step, RECORD_DECIMALS)            # 计算出实际位移量mm
        current_coordinates_x += x_distance_mm                                  # 更新X轴现有位置
        current_coordinates_x = round(current_coordinates_x, RECORD_DECIMALS)   # 限定小数点后8位
        # 线程加锁
        threads_lock.acquire()
        current_coordinates.record('motor_x', current_coordinates_x)            # 执行更新记录
        # 线程解锁
        threads_lock.release()
        print("121:更新后x坐标：%s" % current_coordinates_x)
    else:
        print("123:x轴运动将超出安全范围[%s, %s]，禁止此次运动" % (X_RANGE[0], X_RANGE[1]))
    return


def only_z(coordinate_now, coordinate_target, rpm_max=None):
    """
    接收z轴当前坐标和目标坐标,计算运动距离，指定控制，并更新坐标位置
    z轴运动最高转速可以指定

    Parameters
    ----------
    coordinate_now
        关注点当前坐标
    coordinate_target
        关注点目标坐标
    rpm_max
        运动最高转速设定，未指定按照默认

    """
    current_coordinates_z = current_coordinates.get('motor_z')              # 获取目前主体的坐标
    # 通过现有坐标和目的坐标计算需要走的距离，包含正负
    z_distance = coordinate_target - coordinate_now
    z_target = round(current_coordinates_z + z_distance, 1)              # 计算目标z轴的坐标,round避免往返运算的极小数
    # 判断目标z轴的坐标是否在允许范围内
    if Z_RANGE[0] <= z_target <= Z_RANGE[1]:
        print("142:目前z坐标：%s,位移量：%s" % (coordinate_now, z_distance))
        step_num, unit_step = z.move(z_distance, rpm_max)

        # 更新Z轴坐标
        z_distance_mm = round(step_num * unit_step, RECORD_DECIMALS)            # 计算出实际位移量mm
        current_coordinates_z += z_distance_mm                                  # 更新Z轴现有位置
        current_coordinates_z = round(current_coordinates_z, RECORD_DECIMALS)   # 限定小数点后8位
        # 线程加锁
        threads_lock.acquire()
        current_coordinates.record('motor_z', current_coordinates_z)            # 执行更新记录
        # 线程解锁
        threads_lock.release()
        print("152:更新后z坐标：%s" % current_coordinates_z)
    else:
        print("154:z轴运动将超出安全范围[%s, %s]，禁止此次运动" % (Z_RANGE[0], Z_RANGE[1]))
    return


def only_x1(coordinate_target, rpm_max=None):
    """
        x1轴运动，夹药装置的打开宽度

    Parameters
    ----------
    coordinate_target
        尖端两侧面的距离，与药片板宽度一样时，可以顺利拉回药片板
    rpm_max
        运动最高转速设定，未指定按照默认
    """
    # 1、判断输入的目标宽度是否在允许范围内
    if not (X1_RANGE[0] <= coordinate_target <= X1_RANGE[1]):
        print("165:x1轴运动将超出安全范围[%s, %s]，禁止此次运动" % (X1_RANGE[0], X1_RANGE[1]))
        return
    current_coordinates_x1 = current_coordinates.get('motor_x1')  # 获取目前主体的坐标
    # 2、通过现有坐标和目的坐标计算需要走的距离，包含正负
    x1_distance = coordinate_target - current_coordinates_x1
    print("170:目前x1宽度为：%s,位移量：%s" % (current_coordinates_x1, x1_distance))
    # 3、运动执行
    step_num, unit_step = x1.move(x1_distance, rpm_max)

    # 4、更新x1轴坐标
    x1_distance_mm = round(step_num * unit_step, RECORD_DECIMALS)               # 计算出实际位移量mm
    current_coordinates_x1 += x1_distance_mm                                    # 更新x1轴现有位置
    current_coordinates_x1 = round(current_coordinates_x1, RECORD_DECIMALS)     # 限定小数点后8位
    # 线程加锁
    threads_lock.acquire()
    current_coordinates.record('motor_x1', current_coordinates_x1)  # 执行更新记录
    # 线程解锁
    threads_lock.release()
    print("182:更新后x1宽度：%s" % current_coordinates_x1)
    return


def only_y1(coordinate_now, coordinate_target, rpm_max=None):
    """
        y1轴运动，夹药装置的伸出与缩进

    Parameters
    ----------
    coordinate_now
        关注点当前坐标
    coordinate_target
        关注点目标坐标
    rpm_max
        运动最高转速设定，未指定按照默认
    """
    current_coordinates_y1 = current_coordinates.get('motor_y1')  # 获取目前主体的坐标
    # 通过现有坐标和目的坐标计算需要走的距离，包含正负
    y1_distance = coordinate_target - coordinate_now
    y1_target = round(current_coordinates_y1 + y1_distance, 1)             # 计算目标y1轴的坐标,round避免往返运算的极小数
    # print(y1_target)
    # 判断目标y1轴的坐标是否在允许范围内
    if Y1_RANGE[0] <= y1_target <= Y1_RANGE[1]:
        print("197:目前y1坐标为：%s,位移量：%s" % (current_coordinates_y1, y1_distance))
        # 调用运动程序
        step_num, unit_step = y1.move(y1_distance, rpm_max)

        # 更新y1轴坐标
        y1_distance_mm = round(step_num * unit_step, 8)                     # 计算出实际位移量mm
        print(y1_distance_mm, current_coordinates_y1)
        current_coordinates_y1 += y1_distance_mm                            # 更新y1轴现有位置
        current_coordinates_y1 = round(current_coordinates_y1, 8)           # 限定小数点后8位
        # 线程加锁
        threads_lock.acquire()
        current_coordinates.record('motor_y1', current_coordinates_y1)  # 执行更新记录
        # 线程解锁
        threads_lock.release()
        print("207:更新后y1坐标：%s" % current_coordinates_y1)
    else:
        print("209:y1轴运动将超出安全范围[%s, %s]，禁止此次运动" % (Y1_RANGE[0], Y1_RANGE[1]))
    return


# ############################### 函数说明 ###############################
# wait函数实现去到指定等待工作的位置坐标处
# ########################################################################
def wait():
    # f = open(constant_coordinates_file_path)                            # 打开记录固定坐标的json文件
    # constant_coordinates = json.load(f)                                 # 加载文件中所用内容
    # f.close()                                                           # 关闭文件
    # 获取目前主体的坐标
    current_coordinates_x = current_coordinates.get('motor_x')
    current_coordinates_y = current_coordinates.get('motor_y')
    current_coordinates_z = current_coordinates.get('motor_z')
    target_coordinates_xyz = constant_coordinates.get("motor", "waiting_point")      # 获取等待点的坐标
    print("目前坐标：[%s, %s, %s]，等待工作点坐标：%s"
          % (current_coordinates_x, current_coordinates_y, current_coordinates_z, target_coordinates_xyz))
    only_y(current_coordinates_y, target_coordinates_xyz[1])            # Y轴运动
    only_x(current_coordinates_x, target_coordinates_xyz[0])            # X轴运动
    only_z(current_coordinates_z, target_coordinates_xyz[2])            # Z轴运动


# ############################### 函数说明 ###############################
# check_ready函数实现去到指定等待工作的位置坐标处
# ########################################################################
def check_ready():
    # f = open(constant_coordinates_file_path)                            # 打开记录固定坐标的json文件
    # constant_coordinates = json.load(f)                                 # 加载文件中所用内容
    # f.close()                                                           # 关闭文件
    # 获取目前主体的坐标
    current_coordinates_x = current_coordinates.get('motor_x')
    current_coordinates_y = current_coordinates.get('motor_y')
    current_coordinates_z = current_coordinates.get('motor_z')
    target_coordinates_xyz = constant_coordinates.get("motor", "ready_check_point")      # 获取准备原点检测的坐标
    print("目前坐标：[%s, %s, %s]，准备原点检测坐标：%s"
          % (current_coordinates_x, current_coordinates_y, current_coordinates_z, target_coordinates_xyz))
    only_y(current_coordinates_y, target_coordinates_xyz[1])  # Y轴运动
    only_x(current_coordinates_x, target_coordinates_xyz[0])  # X轴运动
    only_z(current_coordinates_z, target_coordinates_xyz[2])  # Z轴运动


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

    x1_setup_return = x1.setup()
    if not x1_setup_return:
        print('X1轴初始化失败')

    y1_setup_return = y1.setup()
    if not y1_setup_return:
        print('Y1轴初始化失败')
    return True


# 循环部分
def loop():
    # # 获取当前主体夹具前表面坐标
    # the_front_tong = coordinate_converter.body_tong("the_front_y")
    #
    # # 设定的是前面板外表面坐标，因此用[0, 0]柜桶的代替所有
    # ark_barrels_y = ark_barrels_coordinates.get_plate(1, 0)[1]
    # image_recognition_distance = ark_barrels_coordinates.get_plate_y("image_recognition")
    # # 影像识别边坐标 = 目标柜桶y坐标 + 影像识别边距离
    # image_recognition_coordinate = ark_barrels_y + image_recognition_distance
    #
    # only_y(the_front_tong, image_recognition_coordinate)
    # time.sleep(1)

    i = 0
    while i < 1:
        i = i + 1
        only_z(0, 6.7, 10)
        print("暂停")
        time.sleep(0.1)

        only_z(6.7, 10.5, 20)
        print("暂停")
        time.sleep(0.1)

        only_z(10.5, 11.7, 15)
        print("暂停")
        time.sleep(0.1)

        only_z(11.7, 10.5, 15)
        print("暂停")
        time.sleep(0.1)

        only_z(10.5, 0)
        print("暂停")
        print(i)
        time.sleep(1.5)

    # while True:
    #     only_x(0, 1.5927)
    #     print("暂停")
    #     time.sleep(3)
    #
    #     only_x(0, -1.5927)
    #     print("暂停")
    #     time.sleep(3)
        # only_x1(65)
        # print("暂停")
        # time.sleep(2)

    # only_x(0, 80)
    # print("暂停")
    # time.sleep(2)
    # only_x(80, 0, pw)
    # print("暂停")
    # time.sleep(2)

        # 原点定为361.7
        # only_x(361.6, 4000)
        # print("暂停")
        # time.sleep(2)
        #
        # only_x(361.8, 4000)
        # print("暂停")
        # time.sleep(2)
        #
        # i = 0
        # while i < 5:
        #     i = i + 1
        #     only_x((361.7-i*0.2), 4000)
        #     print("暂停")
        #     time.sleep(2)
        #     #
        #     # only_x((361.7+i*0.2), 4000)
        #     # print("暂停")
        #     # time.sleep(2)
        #
        # only_x(361.7, 4000)
        # print("暂停")
        # time.sleep(2)

        # return


# 结束释放
def destroy():
    z.destroy()
    y.destroy()
    x.destroy()
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
