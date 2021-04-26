#!/usr/bin/env python 
# -*- coding:utf-8 -*-
import time
from led.led_class import Led
from rpi_ws281x import Color

# 初始化设定
def setup():
    return True


# 循环部分
def main():
    led_usd = Led()
    led_usd.threading_test()
    while True:
        print("主进程工作中。。。。。")
        time.sleep(2)
        return


# 结束释放
def destroy():
    led_close = Led()
    led_close.color_wipe(Color(0, 0, 0), 10)
    print("关灯...")
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
 