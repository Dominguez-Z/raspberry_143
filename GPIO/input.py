#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  input.py
#      Author:  钟东佐
#       Date        ||      describe
#   2021/11/17      ||  创建输入边缘检测类
#########################################################
import GPIO.define as gpio_define
import RPi.GPIO as GPIO
import time


class Edge(object):
    """
    输入边缘检测，目前主要功能包括 零点，极限，报警
    """
    # 信息
    # back_sleep_time:单位毫秒，检测成功后间隔改时间后放回，且2倍值用于下降沿检测间隔设定，避免多次触发回调函数
    __data = {
        "origin": {
            "pin": gpio_define.INPUT_MOTOR_ORIGIN,
            "back_sleep_time": 500,
            "active_level": True
        },
        "error": {
            "pin": gpio_define.INPUT_ERROR,
            "back_sleep_time": 100,
            "active_level": True
        },
        "y1_limit": {
            "pin": gpio_define.INPUT_Y1_LIMIT,
            "back_sleep_time": 100,
            "active_level": False
        }

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
        使用begin()开启检测，stop()关闭检测，trigger()查询状态

        Parameters
        ----------
        func
            目前允许的有{"origin", "limit", "alm"}
        """
        if self.__init_en:
            if debug:
                print("功能：{0}, self:{1}, {2}\n".format(func, self.__func, self))
            # init
            self.pin = self.__data.get(func)["pin"]     # io口
            self.back_sleep_time = self.__data.get(func)["back_sleep_time"]
            self.fun_str = func                         # 用于打印信息
            self.trigger_signal = False                 # 触发信号
            # 设置该io接口的有效电平和事件跳变沿
            if self.__data.get(func)["active_level"] is True:
                self.active_level = GPIO.PUD_UP
                self.invalid_level = GPIO.PUD_DOWN
                self.io_input_invalid = 0
                self.event_edge = GPIO.RISING
            else:
                self.active_level = GPIO.PUD_DOWN
                self.invalid_level = GPIO.PUD_UP
                self.io_input_invalid = 1
                self.event_edge = GPIO.FALLING

            print(self.pin)
            self.setup()                                # 初始化的时候配置io口
        else:
            # 该功能实例过，不需要初始化
            print("已有注册，跳过初始化")
            pass

    def setup(self):
        """
        设置指定功能的io口数据

        Returns
        -------
        True
            返回真代表初始化正常
        """
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)                                      # Numbers GPIOs by physical location
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=self.invalid_level)     # 设置为输入，因为检测下降沿，设置为上拉
        return True

    def begin(self):
        """
        开启跳变沿检测
        """
        # 对于光耦的信号增加下降边沿检测,开启线程回调
        # bouncetime设定为返回间隔的2倍，防止多次触发回调函数
        GPIO.add_event_detect(self.pin, edge=self.event_edge, callback=self.callback,
                              bouncetime=int(self.back_sleep_time * 2))
        self.trigger_signal = False
        return

    def stop(self):
        """
        取消跳变沿检测事件
        """
        # 移除
        GPIO.remove_event_detect(self.pin)
        self.trigger_signal = False
        return

    def callback(self, channel):
        """
        边沿检测到后的回调函数

        Parameters
        ----------
        channel
            触发的通道
        """
        # 增加抖动检测
        time.sleep(0.01)  # 10毫秒延迟
        if GPIO.input(channel) == self.io_input_invalid:
            # 误触发，返回
            print("误触发了 {} ".format(self.fun_str))
            return

        print("\n################################")
        print("{} 触发了检测".format(self.fun_str))
        print("################################\n")
        self.trigger_signal = True  # 触发信号
        return

    def trigger(self):
        """
        返回触发结果，由此知道是否触发了检测，未触发返回False,触发了返回True
        """
        if self.trigger_signal:
            # 触发信号为真，返回前改变状态，避免误触发
            self.trigger_signal = False
            return True
        return False

    def state(self):
        """
        返回当前GPIO值，0/1
        """
        return GPIO.input(self.pin)


def setup():
    """
    初始化设定
    """

    return True


def main():
    """
    主函数
    """
    # test_1 = Edge(func="origin", debug=True)
    # test_2 = Edge(func="limit", debug=True)
    # test_3 = Edge(func="alm", debug=True)
    # test_4 = Edge(func="alm", debug=True)
    # test_5 = Edge(func="origi", debug=True)
    # print(test_1, test_2, test_3, test_4, test_5)

    # ============== 测试y1_限位开关作用
    y1_limit = Edge(func="y1_limit")
    y1_limit.begin()
    while True:
        if y1_limit.trigger() is True:
            print("到达底端了")
            y1_limit.stop()
        else:
            print("还可以继续退")
        time.sleep(1)

    # print(GPIO.PUD_UP, GPIO.PUD_DOWN, GPIO.PUD_OFF, GPIO.RISING, GPIO.FALLING)


def destroy():
    """
    结束释放
    """
    return


if __name__ == '__main__':  # 程序从这开始
    """
    如果该程序为主程序，程序在此开始运行，若不是不运行，该文件只做函数定义
    """
    # 初始化
    setup_return = setup()
    if setup_return:
        print('始化成功')

    try:
        main()
    except KeyboardInterrupt:  # 当按下 'Ctrl+C', 子函数 destroy()将会运行，用于停止退出
        print("程序已停止退出...")
        destroy()
