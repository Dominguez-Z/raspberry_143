#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  led_class.py
#      Author:  钟东佐
#        Date:  2020/6/4
#    describe:  驱动水平安置的灯带
#########################################################
import time
from rpi_ws281x import PixelStrip, Color
from multiprocessing import Process
import threading
import GPIO.define as gpio_define
# ############################ 常数值设定区域 ############################

# ########################################################################


# 指示命令 ：
# 待命中						standby()
# 取药盒						take_medicine_brick()
# 工作中						working()
# 异常（需维修）				abnormal()
# 没有药盒（需添加药盒）		no_medicine_brick()
# 指定柜桶没有药（需添加药板）	no_medicine(column, row)
# 测试模式						testing
class Led(object):
    def __init__(self):
        # LED 配置:
        LED_COUNT = 120              # 要控制LED的数量.
        LED_PIN = gpio_define.LED_WS2812    # GPIO接口 需要带有PWM功能的 40-pin models: pins 12, 32, 33, 35，BCM：18，12，13，19
        # LED_PIN = 10              # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
        LED_BRIGHTNESS = 150        # 设置LED亮度 (0-255)
        # 以下LED配置无需修改
        LED_FREQ_HZ = 800000        # LED信号频率（以赫兹为单位）（通常为800khz）
        LED_DMA = 10                # 用于生成信号的DMA通道（尝试5）
        LED_INVERT = False          # 反转信号（使用NPN晶体管电平移位时）
        LED_CHANNEL = 0             # set to '1' for GPIOs 13, 19, 41, 45 or 53

        # 创建LED控制对象
        self.strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        # 初始化字典 (在其他函数使用前必须调用一次).
        self.strip.begin()
        print('LED始化成功')

    # 功能一：逐个变指定颜色
    def color_wipe(self, color, wait_ms=50):
        """Wipe color across display a pixel at a time."""
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color)
            self.strip.show()
            time.sleep(wait_ms / 1000.0)

    # 功能二：指定颜色交替闪烁
    def theater_chase(self, color, wait_ms=1000, iterations=10):
        """Movie theater light style chaser animation."""
        for j in range(iterations):
            for q in range(3):
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i + q, color)
                self.strip.show()
                time.sleep(wait_ms / 1000.0)
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i + q, 0)

    # 彩虹颜色计算函数
    def wheel(self, pos):
        """Generate rainbow colors across 0-255 positions."""
        if pos < 85:
            return Color(pos * 3, 255 - pos * 3, 0), str((pos * 3, 255 - pos * 3, 0))
        elif pos < 170:
            pos -= 85
            return Color(255 - pos * 3, 0, pos * 3), str((pos * 3, 255 - pos * 3, 0))
        else:
            pos -= 170
            return Color(0, pos * 3, 255 - pos * 3), str((pos * 3, 255 - pos * 3, 0))

    # 功能三：彩虹色整体统一柔和渐变
    def rainbow(self, wait_ms=20, iterations=1):
        """Draw rainbow that fades across all pixels at once."""
        # for j in range(256 * iterations)              # 这个使得循环颜色的传播方向相反
        for j in range(255 * iterations, -1, -1):
            for i in range(self.strip.numPixels()):
                color, value = self.wheel((i + j) % 255)
                self.strip.setPixelColor(i, color)
                # print((i + j), ((i + j) % 255), value)
                # time.sleep(wait_ms / 1000.0)
            self.strip.show()
            time.sleep(wait_ms / 1000.0)

    # 功能四：彩虹色整体统一柔和渐变，且所有灯刚好是一个彩虹颜色周期
    def rainbow_cycle(self, wait_ms=20, iterations=1):
        """Draw rainbow that uniformly distributes itself across all pixels."""
        for j in range(255 * iterations, -1, -1):
            # print(j)
            for i in range(self.strip.numPixels()):
                color, value = self.wheel((int(i * 256 / self.strip.numPixels()) + j) % 255)
                self.strip.setPixelColor(i, color)
                # print((int(i * 256 / self.strip.numPixels()) + j),
                #       (int(i * 256 / self.strip.numPixels()) + j) % 255,
                #       value)
                # time.sleep(wait_ms / 1000.0)
            self.strip.show()
            time.sleep(wait_ms / 1000.0)

    # 功能五：彩虹色统一闪烁流动变色
    def theater_chase_rainbow(self, wait_ms=50):
        """Rainbow movie theater light style chaser animation."""
        for j in range(255, -1, -1):
            for q in range(3):
                for i in range(0, self.strip.numPixels(), 3):
                    color, value = self.wheel((i + j) % 255)
                    self.strip.setPixelColor(i + q, color)
                self.strip.show()
                time.sleep(wait_ms / 1000.0)
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i + q, 0)

    # 全部灯关闭
    def close(self, color=Color(0, 0, 0), wait_ms=5):
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color)
            time.sleep(wait_ms / 1000.0)
        self.strip.show()

    # 待命中指示：侧边垂直灯带顶端3颗led亮绿色
    def standby(self, color=Color(0, 255, 0), wait_ms=5):
        for i in range(self.strip.numPixels()):
            # print(i)
            if i < 57:
                # print('0')
                self.strip.setPixelColor(i, Color(0, 0, 0))
            else:
                # print('color')
                self.strip.setPixelColor(i, color)
            self.strip.show()
            time.sleep(wait_ms / 1000.0)

    # 取药盒指示：底部水平灯带全亮绿色
    def take_medicine_brick(self, color=Color(0, 255, 0), wait_ms=5):
        for i in range(self.strip.numPixels()):
            if i < 30:
                self.strip.setPixelColor(i, color)
            else:
                self.strip.setPixelColor(i, Color(0, 0, 0))
            self.strip.show()
            time.sleep(wait_ms / 1000.0)

    # 工作中指示：侧边垂直灯带全部亮绿色
    def working(self, color=Color(0, 255, 0), wait_ms=5):
        for i in range(self.strip.numPixels()):
            # print(i)
            if i < 30:
                # print('0')
                self.strip.setPixelColor(i, Color(0, 0, 0))
            else:
                # print('color')
                self.strip.setPixelColor(i, color)
            self.strip.show()
            time.sleep(wait_ms / 1000.0)

    # 异常（需维修）指示：全部灯显示红色
    def abnormal(self, color=Color(255, 0, 0), wait_ms=5):
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color)
            self.strip.show()
            time.sleep(wait_ms / 1000.0)

    # 没有药盒（需添加药盒）指示：底部水平灯带全部显示红色
    def no_medicine_brick(self, color=Color(255, 0, 0), wait_ms=5):
        for i in range(self.strip.numPixels()):
            if i < 30:
                self.strip.setPixelColor(i, color)
            else:
                self.strip.setPixelColor(i, Color(0, 0, 0))
            self.strip.show()
            time.sleep(wait_ms / 1000.0)

    # 指定行列对应灯区域的中心灯是第几颗
    # 行指示5颗灯一格，记录的是中心灯位置
    columns_wheel = {
        "1": 2,
        "2": 6,
        "3": 10,
        "4": 14,
        "5": 17,
        "6": 21,
        "7": 25,
        "8": 29
    }
    # 行指示3颗灯一格，记录的是中心灯位置
    row_wheel = {
        "1": 4,
        "2": 12,
        "3": 19,
        "4": 27
    }

    # 指定柜桶没有药（需添加药板）指示：行列指定位置亮红灯
    def no_medicine(self, column, row, color=Color(255, 0, 0), wait_ms=5):
        print(self.columns_wheel.get(str(column)))
        print(self.row_wheel.get(str(row)))
        for i in range(self.strip.numPixels()):
            # print(i)
            if ((self.columns_wheel.get(str(column)))-1) <= i <= ((self.columns_wheel.get(str(column)))-1) or \
                    ((self.row_wheel.get(str(row)) - 2)+29) <= i <= ((self.row_wheel.get(str(row)) + 2)+29):
                # 上发row加29是因为行列灯是串联的，水平灯带在前，有30颗灯珠
                # print('color')
                self.strip.setPixelColor(i, color)
            else:
                self.strip.setPixelColor(i, Color(0, 0, 0))
                # print('0')
            self.strip.show()
            time.sleep(wait_ms / 1000.0)

    # 测试模式指示：全部显示蓝色
    def testing(self, color=Color(0, 0, 255), wait_ms=5):
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color)
            self.strip.show()
            time.sleep(wait_ms / 1000.0)

    # LED展示程序
    def test(self):
        pass
        # print('Color wipe animations.')
        # self.color_wipe(Color(255, 0, 0))  # Red wipe
        # self.color_wipe(Color(0, 255, 0))  # Blue wipe
        # self.color_wipe(Color(0, 0, 255))  # Green wipe
        # print('Theater chase animations.')
        # self.theater_chase(Color(127, 127, 127))  # White theater chase
        # self.theater_chase(Color(127, 0, 0))  # Red theater chase
        # self.theater_chase(Color(0, 0, 127))  # Blue theater chase
        # print('Rainbow animations.')
        # self.rainbow()
        # self.rainbow_cycle()
        # self.theater_chase_rainbow()

    # 线程控制测试
    def threading_test(self):
        print("LED线程开始")
        t = threading.Thread(target=self.test)
        t.daemon = True
        t.start()
        print("LED线程结束")


# 初始化设定
def setup():
    return True


# 循环部分
def main():
    led_use = Led()

    # print("standby")
    # led_use.standby()
    # time.sleep(3)

    print("take_medicine_brick")
    led_use.take_medicine_brick()
    time.sleep(5)

    # print("working")
    # led_use.working()
    # time.sleep(3)

    print("abnormal")
    led_use.abnormal()
    time.sleep(5)

    # print("no_medicine_brick")
    # led_use.no_medicine_brick()
    # time.sleep(3)

    # print("no_medicine")
    # for i in range(4):
    #     for j in range(8):
    #         led_use.no_medicine(1+1, i+1)
    #         time.sleep(0.1)

    print("testing")
    led_use.testing()
    time.sleep(5)
    # time.sleep(2)
    # led_use.threading_test2()
    while True:
        print("主进程工作中。。。。。")
        time.sleep(2)


# 结束释放
def destroy():
    led_use = Led()
    led_use.close()
    print("关灯...")
    return


# 如果该程序为主程序，程序在此开始运行，若不是不运行，该文件只做函数定义
if __name__ == '__main__':  # Program start from here
    # setup_return = setup()
    # if setup_return:
    #     print('始化成功')
    try:
        main()
    except KeyboardInterrupt:  # 当按下 'Ctrl+C', 子函数 destroy()将会运行，用于停止退出
        print("程序已停止退出...")
        destroy()
 