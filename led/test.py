#!/usr/bin/env python 
# -*- coding:utf-8 -*-
import time
import random
from rpi_ws281x import Adafruit_NeoPixel, Color

# LED 配置:
LED_COUNT = 25          # 要控制LED的数量.
LED_PIN = 18            # GPIO接口 需要带有PWM功能的 40-pin models: pins 12, 32, 33, 35
LED_BRIGHTNESS = 255    # 设置LED亮度 (0-255)
# 以下LED配置无需修改
LED_FREQ_HZ = 800000    # LED信号频率（以赫兹为单位）（通常为800khz）
LED_DMA = 10            # 用于生成信号的DMA通道（尝试5）
LED_INVERT = False      # 反转信号（使用NPN晶体管电平移位时）

# 创建NeoPixel对象
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
# 初始化库
strip.begin()

# 设置整体亮度 关闭LED为0 最亮为255 范围0-255
# 该函数与下面的设置颜色都不会直接对LED进行修改，可以理解为将修改数据保存到缓存区。
# strip.setBrightness(200)


# numPixels()函数介绍：取NeoPixel对象创建时设置的LED数量
for i in range(0, strip.numPixels()):  # 设置个循环(循环次数为LED数量)

    # setPixelColor()函数介绍：设置LED色值(RGB).
    # 参数1：LED 的ID (从0开始, 比如第5个LED)
    # 参数2：RGB色值  Color()RGB转Color值，参数依次为R,G,B
    # 例子：设置第5个LED颜色为红色
    #       strip.setPixelColor(4, Color(255,0,0))
    # 该函数不会直接对LED进行修改，可以理解为将修改数据保存到缓存区。
    strip.setPixelColor(i, Color(0, 0, 255))

    # 提交缓存区的修改数据到WS2812B，以显示效果
    strip.show()

    time.sleep(0.1)  # 延迟0.1秒
