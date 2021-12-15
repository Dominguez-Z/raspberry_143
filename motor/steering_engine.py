#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  steering_engine.py
#      Author:  钟东佐
#       Date        ||      describe
#   2021/05/19      ||  舵机驱动
#########################################################
"""
调用函数 drive 驱动舵机
"""
import RPi.GPIO as GPIO
import time
import signal
import atexit
import wiringpi
import GPIO.define as gpio_define
##########################################################################
# 常数值设定区域
SERVO_PIN = gpio_define.SERVO
# CLOSE_ANGLE = 165
# OPEN_ANGLE = 120

##########################################################################


class Servo(object):
    """ 舵机驱动 """

    __data = {
        "drop": {
            "pin": gpio_define.SERVO,
            "close_angle": 100,
            "open_angle": 50
        },

    }
    # 控制有限的实例
    __instance = []
    __func = []
    __init_en = True

    def __new__(cls, func, debug=False, *args, **kw):
        if func not in cls.__data:
            # 没有数据记录，不允许实例
            print("func的值不在__data记录中,{}".format(list(cls.__data)))
            return None

        if func not in cls.__func:
            # 该功能未被注册过
            cls.__func.append(func)         # 增加已实例的功能记录
            cls.__instance.append(object.__new__(cls, *args, **kw))
            cls.__init_en = True
            i = len(cls.__instance) - 1
            if debug:
                print("cls:{},{}".format(cls.__func, cls.__instance))
        else:
            # 该功能已实例过
            cls.__init_en = False
            i = cls.__func.index(func)
            if debug:
                print("已有实例{}\n".format(cls.__func[i]))
        # print(cls.__instance[i])
        return cls.__instance[i]

    def __init__(self, func, debug=False):
        """

        Parameters
        ----------
        func
            目前允许的有{"drop"}
        """
        if not self.__init_en:
            # 该功能实例过，不需要初始化
            print("已有注册，跳过初始化")
            pass

        else:
            if debug:
                print("功能：{0}, self:{1}, {2}\n".format(func, self.__func, self))
            # init
            self.pin = self.__data.get(func)["pin"]  # io口
            self.close_angle = self.__data.get(func)["close_angle"]
            self.open_angle = self.__data.get(func)["open_angle"]

            self.setup()                                # 初始化的时候配置io口

            # 启动pwm
            self.pwm = GPIO.PWM(self.pin, 50)  # 50HZ
            print(self.pwm)
            self.pwm.start((0.5 + self.close_angle / 90) / 20 * 100)
            time.sleep(0.5)
            self.pwm.ChangeDutyCycle(0)                 # 关闭脉冲防抖

    def setup(self):
        """
        初始化设定

        """
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT, initial=False)


        return True

    def turn_to(self, angle, turn_time=0.5):
        """
        转动到指定角度停下

        Parameters
        ----------
        angle
            目标角度，范围值 0 - 180
        turn_time
            旋转到位需要的时间，默认设置为0.5s

        """
        a = (0.5 + angle / 90) / 20 * 100
        self.pwm.ChangeDutyCycle(a)                 # 设置转动角度
        time.sleep(turn_time)                       # 等该转动到位结束
        self.pwm.ChangeDutyCycle(0)                 # 输出置零，停止脉冲输出
        time.sleep(0.04)

    def drop_medicine(self):
        """
        实现药掉出兜内并随后关闭出药口

        """
        self.turn_to(self.open_angle)
        print(self.open_angle)
        time.sleep(1)
        self.turn_to(self.close_angle)
        print(self.close_angle)
        time.sleep(0.1)
        return


def main():
    """
    主函数

    """
    servo = Servo("drop")
    while True:
        angle = servo.close_angle - servo.open_angle
        # turn_to(CLOSE_ANGLE - angle / 4)
        # servo.turn_to(servo.close_angle - angle / 2, 0.2)
        # turn_to(CLOSE_ANGLE - angle * 3 / 4)

        servo.turn_to(servo.open_angle)
        print("kai")
        time.sleep(0.1)

        servo.turn_to(servo.close_angle)
        print("guan")
        time.sleep(1)


def destroy():
    """ 结束释放 """
    GPIO.cleanup()  # 释放控制


# 如果该程序为主程序，程序在此开始运行，若不是不运行，该文件只做函数定义
if __name__ == '__main__':  # Program start from here
    try:
        main()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child function destroy() will be  executed.
        print("stop...")
        destroy()
