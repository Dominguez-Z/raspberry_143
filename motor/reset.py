#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  reset.py
#      Author:  钟东佐
#       Date        ||      describe
#   2020/12/09      ||  xyz轴红外检测，由于共用一个io通道，将原先分开测试的写在一起。
#   2021/4/1        ||  将main模块中的和reset相关的函数代码整合到该模块中
#########################################################
"""
复位控制模块，调用begin启动复位。
目前各轴的复位方向为：
x - 正，y - 负，z - 负。
复位控制未升级加速算法，升级后使用更为稳妥。目前使用的还是固定速度。

"""
import RPi.GPIO as GPIO
import wiringpi
import time
import motor.x_drive as x
import motor.y_drive as y
import motor.z_drive as z
import JSON.constant_coordinates as constant_coordinates
import JSON.current_coordinates as current_coordinates
# import math

# ################################################# 常数值设定区域 #################################################
RESET = 20      # 光电开关信号接在GPIO20
motor_stop = False   # 设定电机停止标志
# 单位秒，检测成功后间隔改时间后放回，且2倍值用于下降沿检测间隔设定，避免多次触发回调函数
BACK_SLEEP_TIME = 0.5
# ################  设定X轴的参数  #################
X_PUL = 19      # X轴脉冲控制信号,19
X_DIR = 26      # X轴方向控制信号，False是向右，True是向左,26
# 用于控制运动方向
X_LEFT = True
X_RIGHT = False
X_UNIT_STEP_MM = 50.0407 * 1e-3            # 设定单位步长，由实际测了计算获知
# 设定X轴的运动范围，用于红外检测时的最远距离，X_RANGE_MM注意正负，正为向右移动，负为向左移动
X_RANGE_MM = 1100
X_BACK_DISTANCE = 10                            # 检测成功后返回的距离，不需要考虑正负，默认反方向
# ################  设定Y轴的参数  #################
Y_PUL = 8           # Y轴脉冲控制信号
Y_DIR = 7           # Y轴方向控制信号，False是向下，True是向上
# 用于控制运动方向
Y_BACK = True
Y_FRONT = False
Y_UNIT_STEP_MM = 29.96 * 1e-3            # 设定单位步长，由实际测了计算获知，1000细分
# 设定Y轴的运动范围，用于红外检测时的最远距离，Y_RANGE_MM注意正负，正为向右移动，负为向左移动
Y_RANGE_MM = -200
Y_BACK_DISTANCE = 5                             # 检测成功后放回的距离，不需要考虑正负，默认反方向
# ################  设定Z轴的参数  #################
Z_PUL = 11      # Z轴脉冲控制信号,11
Z_DIR = 16      # Z轴方向控制信号，False是向右，True是向左,16
Z_UP = False
Z_DOWN = True
Z_UNIT_STEP_MM = 50.0625 * 1e-3            # 设定单位步长，由实际测了计算获知，1000细分
# 设定Z轴的运动范围，用于红外检测时的最远距离，Z_RANGE_MM注意正负，正为向上移动，负为向下移动
Z_RANGE_MM = -950
Z_BACK_DISTANCE = 10        # 检测成功后放回的距离，初定10mm
# ##################################################################################################################


# /////////////////////////////////////////////////////////////////////////////////////////
# one_step函数说明
# 该函数用于控制树莓派io口输出电平控制电机驱动器的方向和脉冲
# direction为运动方向，step_num为脉冲数
# pulse_width为脉冲宽度，控制运行速度
##########################################################################
# 常数值设定区域
X_PULSE_WIDTH_MAX = 3000                # 设定电机启动最大脉冲宽度，值越大速度越小
X_PULSE_WIDTH_MIN = 800                 # 设定电机启动最小脉冲宽度
X_STEP_NUM_UNIT = X_UNIT_STEP_MM        # 设定单位步长，由实际测了计算获知
Y_PULSE_WIDTH_MAX = 2000                # 设定电机启动最大脉冲宽度，值越大速度越小
Y_PULSE_WIDTH_MIN = 500                 # 设定电机启动最小脉冲宽度
Y_STEP_NUM_UNIT = Y_UNIT_STEP_MM        # 设定单位步长，由实际测了计算获知
Z_PULSE_WIDTH_MAX = 3000                # 设定电机启动最大脉冲宽度，值越大速度越小
Z_PULSE_WIDTH_MIN = 800                 # 设定电机启动最小脉冲宽度
Z_STEP_NUM_UNIT = Z_UNIT_STEP_MM        # 设定单位步长，由实际测了计算获知

# 设定加速完成的速度下限
X_RPM_MIN = 25
Y_RPM_MIN = 40
Z_RPM_MIN = 25
##########################################################################


def x_one_step(direction, step_num, speed=None):
    # 设定运动方向
    if direction == 'x_right':
        GPIO.output(X_DIR, X_RIGHT)   # 设定X轴向右运动
    elif direction == 'x_left':
        GPIO.output(X_DIR, X_LEFT)    # 设定X轴向左运动
    else:
        print('X轴没有指定方向，请检查')
        return
    # X轴运动
    # 1步 = 90um
    if speed == "fast":
        pulse_width_check = X_PULSE_WIDTH_MIN         # 检测时脉冲宽度设定为X轴的启动脉冲
    else:
        pulse_width_check = X_PULSE_WIDTH_MAX         # 检测时脉冲宽度设定为X轴的启动脉冲
    global motor_stop
    motor_stop = False  # 回程前不管电机停止位是什么，先清零，防止未知电位
    print("90:Motor_Stop = False")
    # 控制电机io电平翻转
    for i in range(0, step_num):
        if not motor_stop:
            # 脉冲产生
            # print(i, pulse_width_math)
            # t1 = wiringpi.micros()
            # t1 = wiringpi.micros()
            GPIO.output(X_PUL, False)
            # time.sleep(pulse_width_math*us)
            wiringpi.delayMicroseconds(pulse_width_check)
            # t2 = wiringpi.micros()
            GPIO.output(X_PUL, True)
            # time.sleep(pulse_width_math*us)
            wiringpi.delayMicroseconds(pulse_width_check)
            # print(i, pulse_width_math, t2 - t1)
        elif motor_stop:
            GPIO.output(X_PUL, True)    # 电机脉冲保持高电平，电机停止运动
            motor_stop = False          # 检测到停止信号后，停止信号清零
            return 'stop_success'
        else:
            print("X轴停止信号motor_stop不明确")
    return 'stop_not_success'


def y_one_step(direction, step_num, speed=None):
    # 设定运动方向
    if direction == 'y_front':
        GPIO.output(Y_DIR, Y_FRONT)  # 设定Y轴向前运动
    elif direction == 'y_back':
        GPIO.output(Y_DIR, Y_BACK)  # 设定Y轴向后运动
    else:
        print('Y轴没有指定方向，请检查')
        return
    # Y轴运动
    # 1步 = 90.14um
    if speed == "fast":
        pulse_width_check = Y_PULSE_WIDTH_MIN  # 检测时脉冲宽度设定为Y轴的启动脉冲
    else:
        pulse_width_check = Y_PULSE_WIDTH_MAX     # 检测时脉冲宽度设定为Y轴的启动脉冲
    global motor_stop
    motor_stop = False  # 回程前不管电机停止位是什么，先清零，防止未知电位
    print("132:Motor_Stop = False")
    # 控制电机io电平翻转
    for i in range(0, step_num):
        if not motor_stop:
            # 脉冲产生
            # print(i, pulse_width_math)
            # t1 = wiringpi.micros()
            # t1 = wiringpi.micros()
            GPIO.output(Y_PUL, False)
            # time.sleep(pulse_width_math*us)
            wiringpi.delayMicroseconds(pulse_width_check)
            # t2 = wiringpi.micros()
            GPIO.output(Y_PUL, True)
            # time.sleep(pulse_width_math*us)
            wiringpi.delayMicroseconds(pulse_width_check)
            # print(i, pulse_width_math, t2 - t1)
        elif motor_stop:
            GPIO.output(Y_PUL, True)    # 电机脉冲保持高电平，电机停止运动
            motor_stop = False          # 检测到停止信号后，停止信号清零
            return 'stop_success'
        else:
            print("Y轴停止信号motor_stop不明确")
    return 'stop_not_success'


def z_one_step(direction, step_num, speed=None):
    # 设定运动方向
    if direction == 'z_up':
        GPIO.output(Z_DIR, Z_UP)  # 设定Z轴向上运动
    elif direction == 'z_down':
        GPIO.output(Z_DIR, Z_DOWN)  # 设定Z轴向下运动
    else:
        print('Z轴没有指定方向，请检查')
        return
    # Z轴运动
    if speed:
        pulse_width_check = Z_PULSE_WIDTH_MIN         # 检测时脉冲宽度设定为Z轴的启动脉冲
    else:
        pulse_width_check = Z_PULSE_WIDTH_MAX         # 检测时脉冲宽度设定为Z轴的启动脉冲
    global motor_stop
    motor_stop = False  # 回程前不管电机停止位是什么，先清零，防止未知电位
    print("173:Motor_Stop = False")
    # 控制电机io电平翻转
    for i in range(0, step_num):
        if not motor_stop:
            # 脉冲产生
            # print(i, pulse_width_math)
            # t1 = wiringpi.micros()
            # t1 = wiringpi.micros()
            GPIO.output(Z_PUL, False)
            # time.sleep(pulse_width_math*us)
            wiringpi.delayMicroseconds(pulse_width_check)
            # t2 = wiringpi.micros()
            GPIO.output(Z_PUL, True)
            # time.sleep(pulse_width_math*us)
            wiringpi.delayMicroseconds(pulse_width_check)
            # print(i, pulse_width_math, t2 - t1)
        elif motor_stop:
            GPIO.output(Z_PUL, True)    # 电机脉冲保持高电平，电机停止运动
            motor_stop = False          # 检测到停止信号后，停止信号清零
            return 'stop_success'
        else:
            print("Z轴停止信号motor_stop不明确")
    return 'stop_not_success'
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


def my_callback(RESET):
    """
    边沿检测到后的回调函数, 将停止状态参数motor_stop设置为真

    Parameters
    ----------
    RESET
        指定的通道编号
    """
    global motor_stop
    motor_stop = True               # 将电机停止位置位1,，表示需要停下电机
    print("204:Motor_Stop = True")


def setup():
    """
    reset模块的初始化
    主要设定了复位信号的通道

    Returns
    -------
    True
        返回真代表初始化正常
    """
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)                                  # Numbers GPIOs by physical location
    GPIO.setup(RESET, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # 设置为输入，因为检测下降沿，设置为上拉
    # 对于光耦的信号增加下降边沿检测,开启线程回调
    # bouncetime设定为放回间隔的2倍，防止多次触发回调函数
    GPIO.add_event_detect(RESET, edge=GPIO.RISING, callback=my_callback,
                          bouncetime=int(BACK_SLEEP_TIME*1000*2))
    return True


# /////////////////////////////////////////////////////////////////////////////////////////
# move函数说明
# 各轴距离转步数计算及控制,距离单位为mm
##########################################################################
# 常数值设定区域
X_UNIT_STEP = X_UNIT_STEP_MM           # 设定单位步长，由实际测了计算获知
Y_UNIT_STEP = Y_UNIT_STEP_MM           # 设定单位步长，由实际测了计算获知
Z_UNIT_STEP = Z_UNIT_STEP_MM           # 设定单位步长，由实际测了计算获知
##########################################################################


def x_move(speed=None):
    distance = X_RANGE_MM
    if distance >= 0:
        direction = 'x_left'
        distance_back = -X_BACK_DISTANCE
    elif distance < 0:
        direction = 'x_right'
        distance_back = X_BACK_DISTANCE
    else:
        print("函数需要指定方向和大小，正向右，负向左，单位毫米")
        return
    # 设定单位步长，由实际测了计算获知
    unit_step = X_UNIT_STEP
    # 距离取绝对值再计算步数
    step_num_value = round(abs(distance) / unit_step)
    # 输出计算结果以便检测
    # print("运动距离为：%s" % step_num_value)
    if speed == "fast":
        check_state = x_one_step(direction, step_num_value, speed)    # X轴运动
    else:
        check_state = x_one_step(direction, step_num_value)           # X轴运动
    # check_state: stop_success代表遇到监测点并停下，stop_not_success代表运行到x范围外一直未到监测点
    # 如果检测成功了返回一段距离离开检测物体，避免垂直方向运动撞到
    if check_state == 'stop_success':
        time.sleep(BACK_SLEEP_TIME)
        # x.move(distance_back, 3000)
        x.move(distance_back, X_RPM_MIN)
    else:
        pass
    # 返回检测状态和返回距离
    return check_state, distance_back


def y_move(speed=None):
    distance = Y_RANGE_MM
    if distance >= 0:
        direction = 'y_front'
        distance_back = -Y_BACK_DISTANCE
    elif distance < 0:
        direction = 'y_back'
        distance_back = Y_BACK_DISTANCE
    else:
        print("函数需要指定方向和大小，正向右，负向左，单位毫米")
        return
    # 设定单位步长，由实际测了计算获知
    unit_step = Y_UNIT_STEP
    # 距离取绝对值再计算步数
    step_num_value = round(abs(distance) / unit_step)
    # 输出计算结果以便检测
    # print("运动距离为：%s" % step_num_value)
    if speed == "fast":
        check_state = y_one_step(direction, step_num_value, speed)      # Y轴运动
    else:
        check_state = y_one_step(direction, step_num_value)             # Y轴运动
    # check_state: stop_success代表遇到监测点并停下，stop_not_success代表运行到Y范围外一直未到监测点
    # 如果检测成功了返回一段距离离开检测物体，避免垂直方向运动撞到
    if check_state == 'stop_success':
        time.sleep(BACK_SLEEP_TIME)
        # y.move(distance_back, 2000)
        y.move(distance_back, Y_RPM_MIN)
    else:
        pass
    # 返回检测状态和返回距离
    return check_state, distance_back


def z_move(speed=None):
    distance = Z_RANGE_MM
    if distance >= 0:
        direction = 'z_up'
        distance_back = -Z_BACK_DISTANCE
    elif distance < 0:
        direction = 'z_down'
        distance_back = Z_BACK_DISTANCE
    else:
        print("函数需要指定方向和大小，正向右，负向左，单位毫米")
        return
    # 设定单位步长，由实际测了计算获知
    unit_step = Z_UNIT_STEP
    # 距离取绝对值再计算步数
    step_num_value = round(abs(distance) / unit_step)
    # 输出计算结果以便检测
    # print("运动距离为：%s" % step_num_value)
    if speed == "fast":
        check_state = z_one_step(direction, step_num_value, speed)    # Z轴运动
    else:
        check_state = z_one_step(direction, step_num_value)           # Z轴运动
    # check_state: stop_success代表遇到监测点并停下，stop_not_success代表运行到z范围外一直未到监测点
    # 如果检测成功了返回一段距离离开检测物体，避免垂直方向运动撞到
    if check_state == 'stop_success':
        time.sleep(BACK_SLEEP_TIME)
        # z.move(distance_back, 3000)
        z.move(distance_back, Z_RPM_MIN)
    else:
        pass
    # 返回检测状态和返回距离
    return check_state, distance_back
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


def begin(speed=None):
    """
    用于电机轴坐标复位
    目前包含x, y, z三轴。分别为：
    x - 向正方向移动前往复位点，也就是面对着机子向左
    y - 向负方向移动前往复位点，也就是面对着机子向前
    z - 向负方向移动前往复位点，也就是面对着机子向下

    Parameters
    ----------
    speed
        "fast"：设定为粗定位，快速到达复位点
        默认是精定位，以一个较小的速度慢慢接近复位点，保证接触到后信号的延时控制在脉冲宽度以内。
        一般刚开机先使用粗定位再使用精定位。

    Returns
    -------

    """
    # ############################ 常数值设定区域 ############################
    step_delay = 0.5                     # 步骤间隔时间
    # ########################################################################

    # 复位信号的GPIO通道和状态设定
    setup()

    # y轴向后移动到监测点
    if speed:
        if speed == "fast":
            check_state_y, distance_back_y = y_move(speed)
        else:
            print("y轴矫正参数错误，需要快速输入'fast',默认为慢速")
            return
    else:
        check_state_y, distance_back_y = y_move()
    print(check_state_y)
    time.sleep(step_delay)

    # x轴向右移动到监测点
    if speed:
        if speed == "fast":
            check_state_x, distance_back_x = x_move(speed)
        else:
            print("x轴矫正参数错误，需要快速输入'fast',默认为慢速")
            return
    else:
        check_state_x, distance_back_x = x_move()
    print(check_state_x)
    time.sleep(step_delay)

    # z轴向下移动到监测点
    if speed:
        if speed == "fast":
            check_state_z, distance_back_z = z_move(speed)
        else:
            print("z轴矫正参数错误，需要快速输入'fast',默认为慢速")
            return
    else:
        check_state_z, distance_back_z = z_move()
    print(check_state_z)
    time.sleep(step_delay)

    # 更新body坐标
    begin_check_coordinates_xyz = constant_coordinates.get("motor", "begin_check")   # 获取开始检测后停止点的坐标
    # 执行更新记录
    current_coordinates.record('motor_x', begin_check_coordinates_xyz[0] + distance_back_x)
    current_coordinates.record('motor_y', begin_check_coordinates_xyz[1] + distance_back_y)
    current_coordinates.record('motor_z', begin_check_coordinates_xyz[2] + distance_back_z)

    # 复位成功后释放复位通道
    destroy()
    return


def loop():
    """
    循环部分的代码

    """
    i = 0
    time.sleep(3)
    print("检测程序开始")
    while i < 5:
        i = i + 1
        x.move(10)
        time.sleep(0.5)
        check_state = x_move()
        print(check_state)
        time.sleep(2)


def destroy():
    """
    结束释放io

    """
    # RESET 接在GPIO20，编号为1-40中的38
    GPIO.cleanup(38)              # 释放控制
    return


# 如果该程序为主程序，程序在此开始运行，若不是不运行，该文件只做函数定义
if __name__ == '__main__':  # Program start from here
    x.setup()  # x轴io驱动初始化
    y.setup()  # y轴io驱动初始化
    z.setup()  # z轴io驱动初始化
    setup_return = setup()
    if setup_return:
        print('xyz轴红外检测初始化成功')
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child function destroy() will be  executed.
        print("stop...")
        destroy()
