# !/usr/bin/env python
# -*- coding:utf-8 -*-
#########################################################
#   File name:  step_motor_z.py
#      Author:  钟东佐
#        Date:  2019/07/09
#    describe:  Z轴 28BYJ-48步进电机 底层驱动
#               步进电机分别以单四拍、双四拍、八拍驱动方式驱动，
#               正反转各360度
#########################################################
#########################################################
# 接线方式:
# A ---- 29 ---- OUT1 ---- 橙
# B ---- 31 ---- OUT2 ---- 黄
# C ---- 32 ---- OUT3 ---- 粉（白）
# D ---- 33 ---- OUT4 ---- 蓝
# +   ---- +5V
# -   ---- GND
#########################################################
import RPi.GPIO as GPIO
import time
import wiringpi

# 电机4条控制线连接分配
IN1 = 29
IN2 = 31
IN3 = 32
IN4 = 33
# uchar phasecw[4] ={0x08,0x0c,0x04,0x06,0x02,0x03,0x01,0x09};    # 正转 电机导通相序 D-C-B-A
# uchar phaseccw[4]={0x09,0x01,0x03,0x02,0x06,0x04,0x0c,0x08};    # 反转 电机导通相序 A-B-C-D

# DELAY_NORMAL为正常脉冲间隔，对于控制子函数中直接赋值给delay，调用函数是若需修改可以以实参形式直接复制给delay
DELAY_NORMAL = 3


def set_step(w1, w2, w3, w4):
    GPIO.output(IN1, w1)
    GPIO.output(IN2, w2)
    GPIO.output(IN3, w3)
    GPIO.output(IN4, w4)


def stop():
    set_step(0, 0, 0, 0)


# 8拍驱动，向前
def forward(steps, delay=DELAY_NORMAL):
    for i in range(0, steps):
        set_step(1, 0, 0, 0)
        wiringpi.delay(delay)
        set_step(1, 1, 0, 0)
        wiringpi.delay(delay)
        set_step(0, 1, 0, 0)
        wiringpi.delay(delay)
        set_step(0, 1, 1, 0)
        wiringpi.delay(delay)
        set_step(0, 0, 1, 0)
        wiringpi.delay(delay)
        set_step(0, 0, 1, 1)
        wiringpi.delay(delay)
        set_step(0, 0, 0, 1)
        wiringpi.delay(delay)
        set_step(1, 0, 0, 1)
        wiringpi.delay(delay)


# 8拍驱动，向后
def backward(steps, delay=DELAY_NORMAL):
    for i in range(0, steps):
        set_step(0, 0, 0, 1)
        wiringpi.delay(delay)
        set_step(0, 0, 1, 1)
        wiringpi.delay(delay)
        set_step(0, 0, 1, 0)
        wiringpi.delay(delay)
        set_step(0, 1, 1, 0)
        wiringpi.delay(delay)
        set_step(0, 1, 0, 0)
        wiringpi.delay(delay)
        set_step(1, 1, 0, 0)
        wiringpi.delay(delay)
        set_step(1, 0, 0, 0)
        wiringpi.delay(delay)
        set_step(1, 0, 0, 1)
        wiringpi.delay(delay)


# /////////////////////////////////////////////////////////////////////////////////////////
# 4拍驱动，direction为方向，z_forward 为向前，z_backward 为向后
# delay为脉冲间隔，delayMicroseconds是以us为单位，delay是以ms为单位
def step_drive(direction, step_num, delay=DELAY_NORMAL):
    # 向前运动
    if direction == 'z_forward':
        for i in range(0, step_num):
            set_step(0, 1, 1, 0)
            wiringpi.delay(delay)
            set_step(0, 0, 1, 1)
            wiringpi.delay(delay)
            set_step(1, 0, 0, 1)
            wiringpi.delay(delay)
            set_step(1, 1, 0, 0)
            wiringpi.delay(delay)
    # 向后运动
    elif direction == 'z_backward':
        for i in range(0, step_num):
            set_step(1, 1, 0, 0)
            wiringpi.delay(delay)
            set_step(1, 0, 0, 1)
            wiringpi.delay(delay)
            set_step(0, 0, 1, 1)
            wiringpi.delay(delay)
            set_step(0, 1, 1, 0)
            wiringpi.delay(delay)
    # 没有设定方向直接返回并提示
    else:
        print('Z轴没有指定方向，请检查')
        return
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


# 初始化设定
def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)  # Numbers GPIOs by physical location
    GPIO.setup(IN1, GPIO.OUT)  # Set pin's mode is output
    GPIO.setup(IN2, GPIO.OUT)
    GPIO.setup(IN3, GPIO.OUT)
    GPIO.setup(IN4, GPIO.OUT)

    return True


# /////////////////////////////////////////////////////////////////////////////////////////
# move函数说明
# Z轴距离转步数计算及控制,距离单位为mm
##########################################################################
# 常数值设定区域
UNIT_STEP = 122.9 * 1e-3           # 设定单位步长，由实际测了计算获知
HYSTERISIS_ERROR = 1.8              # 设定Z轴的回程误差，当反向改变的时候需要加上该段距离
##########################################################################


def move(distance, dir_change_state):
    # 设定单位步长，由实际测了计算获知
    unit_step = UNIT_STEP
    hysterisis_error = HYSTERISIS_ERROR
    # 距离取绝对值再计算步数
    # 判断方向是否有改变，有改变了加入回程误差
    if dir_change_state == 'change_dir':
        step_num_value = round((abs(distance) + hysterisis_error) / unit_step)
    elif dir_change_state == 'no_change_dir':
        step_num_value = round(abs(distance) / unit_step)
    else:
        print('没有指定Z轴运动方向是否改变，请检查代码')
        return
    # 根据距离的正负确定运动方向
    if distance >= 0:
        direction = 'z_forward'
    elif distance < 0:
        direction = 'z_backward'
    else:
        print("函数需要指定方向和大小，正向前，负向后，单位毫米")
        return
    # 输出计算结果以便检测
    print("166：%s运动距离为：%s" % (direction, step_num_value))
    step_drive(direction, step_num_value)  # Z轴运动
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


# 循环部分
def loop():
    move(156.4, 'change_dir')
    move(-156.4, 'change_dir')
    # move('z_backward', 'no_change_dir', 0.5)
    # while True:
        # move('z_forward', 'change_dir', 11.1)
        # time.sleep(5)
        #
        # time.sleep(5)
        # print("stop...")
        # stop()
        # time.sleep(5)
        #
        # print("backward...")
        # # backward_4(768)  # 512 steps --- 360 angle，0.003
        #
        # print("stop...")
        # stop()  # stop
        # time.sleep(3)  # sleep 3s
        #
        # print("forward...")
        # # forward_4(768)\


# 结束释放
def destroy():
    # GPIO.setmode(GPIO.BOARD)  # Numbers GPIOs by physical location
    GPIO.cleanup()  # Release resource


if __name__ == '__main__':  # Program start from here
    setup_return = setup()
    if setup_return:
        print('Z轴初始化成功')
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child function destroy() will be  executed.
        destroy()
