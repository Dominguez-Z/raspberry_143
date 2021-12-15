#!/usr/bin/env python
# coding = utf-8
#########################################################
#   File name: 57_step_Motor_XY.py
#      Author: 钟东佐
#        Date: 2019/07/03
#########################################################
import RPi.GPIO as GPIO
import wiringpi
import time
import math

Y_PUL = 7  # Y轴脉冲控制信号
Y_DIR = 8  # Y轴方向控制信号
X_PUL = 3  # X轴脉冲控制信号
X_DIR = 5  # X轴方向控制信号
us = 0.000001   # 微秒的乘数
ms = 0.001      # 毫秒的乘数
X = 0
Y = 1
x_left = 0b00
x_right = 0b01
y_up = 0b10
y_down = 0b11


def one_step(axis, direction, step_num, pulse_width):   # time.sleep的参数最小为0.000001，但是宽度为60到80us不等。
                                                        # axis为运动轴选择，direction为运动方向，step_num为脉冲数
                                                        # pulse_width为脉冲宽度，控制运行速度

    # 设定运动方向
    if direction == x_right:
        GPIO.output(X_DIR, False)   # 设定X轴向右运动
    elif direction == x_left:
        GPIO.output(X_DIR, True)    # 设定X轴向左运动
    elif direction == y_up:
        GPIO.output(Y_DIR, False)   # 设定Y轴向上运动
    elif direction == y_down:
        GPIO.output(Y_DIR, True)    # 设定Y轴向下运动
    else:
        GPIO.output(X_DIR, False)   # 设定X轴向右运动
        GPIO.output(Y_DIR, False)   # 设定Y轴向上运动

    # X轴运动
    # 1步 = 90um
    # pulse_width最低大概是50
    if axis == X:
        step_num_change_width = 1 / 10  # 设定加速或减速分别占整个行程的比例，范围0~1
        pulse_width_max = 250  # 设定电机启动最大脉冲宽度，值越大速度越小
        step_num_min = 100      # 设定有加减速效果的最小步数，步数小于该值时脉冲宽度设定为最大值
        if pulse_width > pulse_width_max or pulse_width < 0:
            pulse_width = pulse_width_max
        step_num_speedup = step_num * step_num_change_width  # 加速停止点
        step_num_speeddown = step_num * (1 - step_num_change_width)  # 减速启动点
        pulse_width_change = pulse_width_max - pulse_width  # 脉冲宽度变化值

        for i in range(0, step_num):
            if step_num < step_num_min:
                pulse_width_math = pulse_width_max
            else:
                if i < step_num_speedup:
                    x = math.pi * i / (step_num * step_num_change_width)
                elif step_num_speedup <= i < step_num_speeddown:
                    x = math.pi
                elif step_num_speeddown <= i <= step_num:
                    x = math.pi * (1 + (i - step_num_speeddown) / (step_num * step_num_change_width))
                amplitude = (math.cos(x) + 1) / 2
                pulse_width_math = int(pulse_width_change * amplitude + pulse_width)
            # 脉冲产生
            # print(i, pulse_width_math)
            #t1 = wiringpi.micros()
            #t1 = wiringpi.micros()
            wiringpi.delayMicroseconds(pulse_width_math)
                    #time.slee p(pulse_width_math*us)
            GPIO.output(X_PUL, False)
            #t2 = wiringpi.micros()
            wiringpi.delayMicroseconds(pulse_width_math)
                    #time.sleep(pulse_width_math*us)
            GPIO.output(X_PUL, True)
            #print(i, pulse_width_math, t2 - t1)
    # Y轴运动
    # pulse_width向上最低大概是200
    elif axis == Y:
        step_num_change_width = 1 / 10  # 设定加速或减速分别占整个行程的比例，范围0~1
        pulse_width_max = 600  # 设定电机启动最大脉冲宽度，值越大速度越小
        step_num_min = 100  # 设定有加减速效果的最小步数，步数小于该值时脉冲宽度设定为最大值
        if pulse_width > pulse_width_max or pulse_width < 0:
            pulse_width = pulse_width_max
        step_num_speedup = step_num * step_num_change_width  # 加速停止点
        step_num_speeddown = step_num * (1 - step_num_change_width)  # 减速启动点
        pulse_width_change = pulse_width_max - pulse_width  # 脉冲宽度变化值

        for i in range(0, step_num):
            if step_num < step_num_min:
                pulse_width_math = pulse_width_max
            else:
                if i < step_num_speedup:
                    x = math.pi * i / (step_num * step_num_change_width)
                elif step_num_speedup <= i < step_num_speeddown:
                    x = math.pi
                elif step_num_speeddown <= i <= step_num:
                    x = math.pi * (1 + (i - step_num_speeddown) / (step_num * step_num_change_width))
                amplitude = (math.cos(x) + 1) / 2
                pulse_width_math = int(pulse_width_change * amplitude + pulse_width)
            #print(i, pulse_width_math)
            #t1 = wiringpi.micros()
            wiringpi.delayMicroseconds(pulse_width_math)
                #time.sleep(pulse_width_math * us)
            GPIO.output(Y_PUL, False)
            #t2 = wiringpi.micros()
            wiringpi.delayMicroseconds(pulse_width_math)
                #time.sleep(pulse_width_math * us)
            GPIO.output(Y_PUL, True)
            #print(i, pulse_width_math, t2 - t1)


def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)    # Numbers GPIOs by physical location
    GPIO.setup(X_PUL, GPIO.OUT)   # Set pin's mode is output
    GPIO.setup(X_DIR, GPIO.OUT)
    GPIO.setup(Y_PUL, GPIO.OUT)  # Set pin's mode is output
    GPIO.setup(Y_DIR, GPIO.OUT)


def loop():
    print("pulse...")
    while True:

        one_step(X, x_right, 800, 50)  # X轴向右运动15000步
        time.sleep(2)  # 延时暂停
        #one_step(Y, y_up, 8000, 250)  # Y轴向上运动15000步
        #time.sleep(50 * ms)  # 延时暂停
        
        one_step(X, x_left, 800, 50)  # X轴向左运动15000步
        time.sleep(2)  # 延时暂停

        # one_step(y, y_up, 8000, 200)  # Y轴向上运动10000步
        # time.sleep(1000 * ms)  # 延时暂停
        #one_step(Y, y_down, 8000, 100)  # Y轴向下运动10000步
        #time.sleep(1000 * ms)  # 延时暂停

        '''
        for i in range(0, 1000):
            one_step(x, x_right, 8)     # X轴向右运动15000步
            #time.sleep(1 * ms)           # 延时暂停
            one_step(y, y_up, 8)        # Y轴向上运动10000步
            #time.sleep(1 * ms)           # 延时暂停
        time.sleep(1000 * ms)           # 延时暂停
        for i in range(0, 1000):
            one_step(x, x_left, 8)      # X轴向左运动15000步
            #time.sleep(1 * ms)           # 延时暂停
            one_step(y, y_down, 8)      # Y轴向下运动10000步
            #time.sleep(1 * ms)           # 延时暂停
        time.sleep(1000 * ms)           # 延时暂停
        '''

def destroy():
    GPIO.output(X_DIR, False)
    GPIO.output(X_PUL, False)
    GPIO.output(Y_DIR, False)
    GPIO.output(Y_PUL, False)
    GPIO.cleanup()  # Release resource


if __name__ == '__main__':  # Program start from here
    setup()
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child function destroy() will be  executed.
        print("stop...")
        destroy()
