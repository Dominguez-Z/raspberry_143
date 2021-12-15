#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  main.py
#      Author:  钟东佐
#        Date:  2020/03/20
#    describe:  树莓派主函数,1.143,密码jmyxjmyx
#########################################################
import JSON.current_coordinates as current_coordinates
import JSON.constant_coordinates as constant_coordinates
import electromagnet.strike_drug_drive as strike_drug
import motor.y_drive as y
import motor.x_drive as x
import motor.z_drive as z
import motor.y1_drive as y1
import motor.x1_drive as x1
import motor.go as go
import motor.check as check
import motor.test_take_medicine as take_medicine
import check.ark_barrels as ark_barrels_check
# import  medicine.press_medicine_capsule as press_medicine_capsule
# import medicine.take_medicine as take
import medicine.jump as jump
import medicine.bottle as bottle
import medicine.plate as plate
import time
# ############################ 常数值设定区域 ############################

# ########################################################################


# 主函数的初始化操作，主要包含各模块的初始化setup
def setup():
    z_setup_return = z.setup()
    if not z_setup_return:
        print('Z轴初始化失败')
        return False

    x_setup_return = x.setup()
    if not x_setup_return:
        print('X轴初始化失败')
        return False

    y_setup_return = y.setup()
    if not y_setup_return:
        print('Y轴初始化失败')
        return False

    x1_setup_return = x1.setup()
    if not x1_setup_return:
        print('X1轴初始化失败')
        return False

    y1_setup_return = y1.setup()
    if not y1_setup_return:
        print('Y1轴初始化失败')
        return False

    strike_drug_setup_return = strike_drug.setup()
    if not strike_drug_setup_return:
        print('打药继电器初始化失败')
        return False

    x_check_setup_return = check.setup()
    if not x_check_setup_return:
        print('xyz轴红外检测初始化失败')
        return False

    return True


# ############################### 函数说明 ###############################
# begin_check: 开机xy轴检测并移动到指定位置
# ########################################################################
# ############################ 常数值设定区域 ############################
BEGIN_CHECK_DELAY = 0.5
# ########################################################################


def begin_check(speed=None):
    time.sleep(BEGIN_CHECK_DELAY)

    # y轴向后移动到监测点
    if speed:
        if speed == "fast":
            check_state_y, distance_back_y = check.y_move(speed)
        else:
            print("y轴矫正参数错误，需要快速输入'fast',默认为慢速")
            return
    else:
        check_state_y, distance_back_y = check.y_move()
    print(check_state_y)
    time.sleep(BEGIN_CHECK_DELAY)

    # x轴向右移动到监测点
    if speed:
        if speed == "fast":
            check_state_x, distance_back_x = check.x_move(speed)
        else:
            print("x轴矫正参数错误，需要快速输入'fast',默认为慢速")
            return
    else:
        check_state_x, distance_back_x = check.x_move()
    print(check_state_x)
    time.sleep(BEGIN_CHECK_DELAY)

    # z轴向下移动到监测点
    if speed:
        if speed == "fast":
            check_state_z, distance_back_z = check.z_move(speed)
        else:
            print("z轴矫正参数错误，需要快速输入'fast',默认为慢速")
            return
    else:
        check_state_z, distance_back_z = check.z_move()
    print(check_state_z)
    time.sleep(BEGIN_CHECK_DELAY)

    # 更新body坐标
    begin_check_coordinates_xyz = constant_coordinates.get("motor", "begin_check")   # 获取开始检测后停止点的坐标
    # 执行更新记录
    current_coordinates.record('motor_x', begin_check_coordinates_xyz[0] + distance_back_x)
    current_coordinates.record('motor_y', begin_check_coordinates_xyz[1] + distance_back_y)
    current_coordinates.record('motor_z', begin_check_coordinates_xyz[2] + distance_back_z)


# 主函数循环
def main():
    # begin_check("fast")
    # begin_check()                                   # 各轴到达传感器监测点
    # go.wait()  # 去到工作等待点
    # return

    # 摇药部分测试
    # bottle.take_medicine(0, 0, 3)
    # time.sleep(1)

    # 测试取药
    plate.do_take(6924168200093, 1, 2)

    # 走三个柜桶
    # while True:
    #     jump.ark_barrel(0, 0)
    #     time.sleep(2)
    #     jump.ark_barrel(3, 7)
    #     time.sleep(2)
    #     jump.ark_barrel(0, 7)
    #     time.sleep(2)
    #     jump.ark_barrel(3, 0)
    #     time.sleep(2)

    """
    while True:
        # time.sleep(3)
        # go.check_ready()                                # 去到准备原点检测的位置
        # begin_check("fast")
        # begin_check()                                   # 各轴到达传感器监测点
        bottle.rotate()
        time.sleep(1)
    """
    # 测试打药部分
    """
    jump.strike_drug_ready()                        # 去打药准备点
    go.wait()                                       # 去到工作等待点
    
    jump.ark_barrel(3, 4)
    i = 0
    time.sleep(1)
    while i < 10:
        print(i)
        i = i + 1
        take_medicine.do_take()                         # 等待点去拿药并返回等待点
        time.sleep(1)
        take_medicine.do_back()                         # 将药从等待点放置回药板柜
        time.sleep(1)
    """

    # ark_barrels_check.run_all()                     # 各柜桶检测走一遍，确定柜子位置和运动正常
    # jump.ark_barrel(28)
    # bottle.take(28)
    # y.move(-3.91)
    # time.sleep(1)
    # for i in range(1, 3):
    #     press_medicine_capsule.medicine(i)
    #     time.sleep(1)
    return


# 退出程序前的关闭操作
def destroy():
    z.destroy()
    y.destroy()
    x.destroy()
    check.destroy()


# 如果该程序为主程序，程序在此开始运行，若不是不运行，该文件只做函数定义
if __name__ == '__main__':
    main_setup_return = setup()
    if not main_setup_return:
        print('主函数初始化失败')

    try:
        main()

    except KeyboardInterrupt:  # 当按下 'Ctrl+C', 子函数 destroy()将会运行，用于停止退出
        print("主函数退出")
        destroy()
