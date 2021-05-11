#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  main.py
#      Author:  钟东佐
#        Date:  2020/03/20
#    describe:  树莓派主函数,1.143,密码jmyxjmyx
#########################################################
import main_h
import medicine.plate as plate
import motor.reset as motor_reset
import medicine.jump as jump
import time


# 主函数循环
def main():
    motor_reset.begin("fast")
    motor_reset.begin()                                   # 各轴到达传感器监测点
    # go.wait()  # 去到工作等待点
    # return

    # 摇药部分测试
    # bottle.take_medicine(0, 0, 3)
    # time.sleep(1)


    # 测试取药
    # 黄连上清片
    # plate.do_take(6924168200093, 1, 5)
    # plate.do_back(6924168200093, 1, 5)
    # 丢掉药板
    # plate.throw_away()

    # 黄连上清片
    # plate.do_take(6924168200093, 1, 6)
    # 丢掉药板
    # plate.throw_away()

    # 复方血栓通胶囊
    # plate.do_take(6902170000238, 2, 5)
    # 丢掉药板
    # plate.throw_away()

    # 牛黄上清片
    # plate.do_take(6921314097279, 1, 7)
    # plate.do_back(6921314097279, 1, 7)
    # 丢掉药板
    # plate.throw_away()

    # 牛黄上清片
    # plate.do_take(6921314097279, 2, 1)
    # 丢掉药板
    # plate.throw_away()

    # 甲钴胺片
    # plate.do_take(6936660900203, 3, 5)
    # 丢掉药板
    # plate.throw_away()

    # jump.ark_barrel(1, 2)
    #     time.sleep(2)

    # 测试打药
    # plate.strike_drug_ready(1)

    # 走三个柜桶
    # while True:
    #     jump.ark_barrel(0, 0)
    #     time.sleep(2)
    #     jump.ark_barrel(3, 7)
    #     time.sleep(2)
    #     jump.ark_barrel(0, 7)
    #     time.sleep(2)
    #     jump.ark_barrel(3, 0)
    #     time.sleep(2)

    # i = 0
    # while True:
        # time.sleep(3)
        # go.check_ready()                                # 去到准备原点检测的位置
        # begin_check("fast")
        # begin_check()                                   # 各轴到达传感器监测点
        # bottle.rotate()
        # time.sleep(1)
        # print(int(i))
        # time.sleep(0.2)
        # i += 0.2

    # 测试打药部分
    #
    # jump.strike_drug_ready()                        # 去打药准备点
    # go.wait()                                       # 去到工作等待点
    #
    # jump.ark_barrel(3, 4)
    # i = 0
    # time.sleep(1)
    # while i < 10:
    #     print(i)
    #     i = i + 1
    #     take_medicine.do_take()                         # 等待点去拿药并返回等待点
    #     time.sleep(1)
    #     take_medicine.do_back()                         # 将药从等待点放置回药板柜
    #     time.sleep(1)
    #

    # ark_barrels_check.run_all()                     # 各柜桶检测走一遍，确定柜子位置和运动正常
    # jump.ark_barrel(28)
    # bottle.take(28)
    # y.move(-3.91)
    # time.sleep(1)
    # for i in range(1, 3):
    #     press_medicine_capsule.medicine(i)
    #     time.sleep(1)
    return


if __name__ == '__main__':
    """
    如果该程序为主程序，程序在此开始运行，若不是不运行，该文件只做函数定义
    
    """
    main_setup_return = main_h.setup()
    if not main_setup_return:
        print('主函数初始化失败')

    try:
        main()

        # 主函数运行结束退出
        main_h.destroy()

    except KeyboardInterrupt:  # 当按下 'Ctrl+C', 子函数 destroy()将会运行，用于停止退出
        main_h.destroy()
