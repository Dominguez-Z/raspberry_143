#!/usr/bin/env python
#########################################################
#   File name: step_Motor_switch.py
#      Author: ZDZ
#        Date: 2019/01/23
#########################################################
import RPi.GPIO as GPIO
import time

PUL = 11            # pin11
DIR = 13
speed_Pin = 22      # 光电开关信号接在pin22, GPIO_GEN6
uS = 0.000001       # 微秒的乘数
mS = 0.001          # 毫秒的乘数
Motor_Stop = False   # 设定电机停止标志
# edge_time = 0

def pulse_82us(duration):         # width的大小最小为0.000001，但是宽度为60到80us不等。
    for i in range(0, int(duration / (0.000082*2) ) ):      # duration为脉冲持续时间
        time.sleep(0.0004)
        GPIO.output(PUL, False)
        time.sleep(0.0004)
        GPIO.output(PUL, True)

#各IO口初始化
def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)    # Numbers GPIOs by physical location
    GPIO.setup(PUL, GPIO.OUT)   # 脉冲控制位
    GPIO.setup(DIR, GPIO.OUT)   # 方向控制位
    GPIO.setup(speed_Pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)   # 设定光耦脉冲输入位，并上拉
    GPIO.add_event_detect(speed_Pin, edge=GPIO.BOTH, callback=my_callback)  # 对于光耦的信号增加边沿检测

# 边沿检测到后的回调函数
def my_callback(speed_Pin):
    global Motor_Stop
    Motor_Stop = True               #将电机停止位置位1,，表示需要停下电机
    print("Motor_Stop = True")


#循环主函数
def loop():
    print("test beginning...")
    while True:
        GPIO.output(DIR, True)      # 设定反方向
        pulse_82us(0.5)             # 产生周期为2*82us的脉冲信号
        time.sleep(50 * mS)

        GPIO.output(DIR, False)     # 设定正方向
        global Motor_Stop
        Motor_Stop = False          # 回程前不管电机停止位是什么，先清零，防止未知电位
        print("Motor_Stop = False")
        #pulse_82us(0.5)            # 产生周期为2*82us的脉冲信号
        print("back now")
        print("...")
        while not Motor_Stop:       #时刻检测是否需要到达了停止点
            pulse_82us(0.001)       #没有遍持续运行
        print("back over")
        time.sleep(50*mS)           # 延时暂停


#退出程序释放IO
def destroy():
    GPIO.output(DIR, False)         # 电机脉冲位拉低
    GPIO.output(PUL, False)         # 电机方向位拉低
    GPIO.cleanup()  # Release resource  # 释放所有IO口

#程序从此处开始
if __name__ == '__main__':          # Program start from here
    setup()                         # 初始化各接口
    try:
        loop()
    except KeyboardInterrupt:       # When 'Ctrl+C' is pressed, the child function destroy() will be  executed.
        print("stop...")
        destroy()



