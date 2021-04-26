#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  .py
#      Author:  钟东佐
#        Date:  2020/6/5
#    describe:  NeoPixel library strandtest example
#               Direct port of the Arduino NeoPixel library strandtest example.
#               Showcases various animations on a strip of NeoPixels.
#########################################################
import time
from rpi_ws281x import PixelStrip, Color
import argparse
# ############################ 常数值设定区域 ############################
# LED strip configuration:
LED_COUNT = 60        # Number of LED pixels.
LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 50  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
# ########################################################################


# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)


def theaterChase(strip, color, wait_ms=1000, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, color)
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, 0)


def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0), str((pos * 3, 255 - pos * 3, 0))
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3), str((pos * 3, 255 - pos * 3, 0))
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3), str((pos * 3, 255 - pos * 3, 0))


def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    # for j in range(256 * iterations)              # 这个使得循环颜色的传播方向相反
    for j in range(255 * iterations, -1, -1):
        for i in range(strip.numPixels()):
            color, value = wheel((i + j) % 255)
            strip.setPixelColor(i, color)
            # print((i + j), ((i + j) % 255), value)
            # time.sleep(wait_ms / 1000.0)
        strip.show()
        time.sleep(wait_ms / 1000.0)


def rainbowCycle(strip, wait_ms=20, iterations=1):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(255 * iterations, -1, -1):
        print(j)
        for i in range(strip.numPixels()):
            color, value = wheel((int(i * 256 / strip.numPixels()) + j) % 255)
            strip.setPixelColor(i, color)
            print((int(i * 256 / strip.numPixels()) + j),
                  (int(i * 256 / strip.numPixels()) + j) % 255,
                  value)
            # time.sleep(wait_ms / 1000.0)
        strip.show()
        time.sleep(wait_ms / 1000.0)


def theater_chase_rainbow(strip, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    for j in range(255, -1, -1):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                color, value = wheel((i + j) % 255)
                strip.setPixelColor(i + q, color)
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, 0)

# 初始化设定
def setup():
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    # Create NeoPixel object with appropriate configuration.
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()

    print('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')
    return True, strip, args


# 循环部分
def main(strip):
    while True:
        theater_chase_rainbow(strip)
        # print('Color wipe animations.')
        # colorWipe(strip, Color(255, 0, 0))  # Red wipe
        # colorWipe(strip, Color(0, 255, 0))  # Blue wipe
        # colorWipe(strip, Color(0, 0, 255))  # Green wipe
        # print('Theater chase animations.')
        # theaterChase(strip, Color(127, 127, 127))  # White theater chase
        # theaterChase(strip, Color(127, 0, 0))  # Red theater chase
        # theaterChase(strip, Color(0, 0, 127))  # Blue theater chase
        # print('Rainbow animations.')
        # rainbow(strip)
        # rainbowCycle(strip)
        # theaterChaseRainbow(strip)
        return



# 结束释放
def destroy(args):
    if args.clear:
        colorWipe(strip, Color(0, 0, 0), 10)
        print("关灯...")
    return


# 如果该程序为主程序，程序在此开始运行，若不是不运行，该文件只做函数定义
if __name__ == '__main__':  # Program start from here
    setup_return, strip, args = setup()
    if setup_return:
        print('始化成功')
    try:
        main(strip)
    except KeyboardInterrupt:  # 当按下 'Ctrl+C', 子函数 destroy()将会运行，用于停止退出
        print("程序已停止退出...")
        destroy(args)
 