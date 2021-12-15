#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  main.py
#      Author:  钟东佐
#        Date:  2020/03/20
#    describe:  树莓派主函数,1.143,密码jmyxjmyx
#########################################################
import main_h
import motor.go as go
import check.ark_barrels as check_ark
import medicine.plate as plate
import medicine.drop as drop
import motor.reset as motor_reset
import medicine.jump as jump
import medicine.bottle as bottle
import motor.lmr_drive as lmr
import electromagnet.strike_drug_drive as strike
# import check.panel_standard as panel_standard
import time


def video_introduction():
    """
    控制介绍视频的运动
    """
    # 1、药板环节
    # 主要包括两种药：
    # 1）黄连上清片、1-5、6924168200093
    # 2）牛黄上清片、1-7、6921314097279
    # 都进入[1, 0]号药盒组的 3号位
    drop_info = {
        "box_matrix": [1, 1],
        "num": 2
    }
    plate_info = {
        "1": {
            "num": 6924168200093,
            "row": 1,
            "line": 5,
            # "strike_drug": [11, 9.85]
            "strike_drug": [10.5, 75.5]
        },
        "0": {
            "num": 6921314097279,
            "row": 1,
            "line": 3,
            "strike_drug": [9.7, 10.4]
        }
    }
    sleep_time = 1

    for i in range(1):
        plate_info_now = plate_info[str(i)]
        # # 1.0 柜桶对位
        # check_ark.param_correction(plate_info_now["num"], plate_info_now["row"], plate_info_now["line"])

        # 1.1 取药板
        do_take_succeed = plate.do_take(plate_info_now["num"], plate_info_now["row"], plate_info_now["line"])
        if not do_take_succeed:
            # 取药有问题
            main_h.error_message("取药板")
        time.sleep(sleep_time)

        # 1.2 打药
        plate.strike_drug(plate_info_now["num"], parts_num=1, num_start=11, strike_num=2, direction=1)
        time.sleep(sleep_time)

        # 1.3 掉药
        drop.do(drop_info["box_matrix"], drop_info["num"])
        time.sleep(sleep_time)

        # 1.4 放回药板
        do_back_succeed = plate.do_back(plate_info_now["num"], plate_info_now["row"], plate_info_now["line"])
        if not do_back_succeed:
            # 放药板有问题
            main_h.error_message("放药板")
        time.sleep(sleep_time)

    # 2、摇药环节
    # 主要包括一种药
    # 2.1 摇药
    i = 0
    succeed_count = 0
    sum = 200
    count = 50
    while i < 1:
        i += 1
        buffer_mode = int(2 - (count // ((sum + 3) // 3)))      # 3级别
        # buffer_mode = int(3 - (count // ((sum + 1) / 4)))     # 4级别
        # # ============= 测试
        # count -= 1
        # print(buffer_mode, i)
        # # ============= 模块
        state, num = bottle.take_medicine(0, 1, num_push_out=2, mode=buffer_mode)
        time.sleep(sleep_time)
        if state is "succeed":
            succeed_count += 1
            count -= 1
        print("\n")
        print("###########")
        print("目前成功次数为%s，总次数为%s" % (succeed_count, i))
        print("###########\n")

    # i = 0
    # succeed_count = 0
    # sum = 200
    # count = 99
    # while i < 1:
    #     i += 1
    #     buffer_mode = int(3 - (count // ((sum+1)/4)))
    #     state, num = bottle.take_medicine(0, 1, 3, mode=buffer_mode)
    #     time.sleep(sleep_time)
    #     if state is "succeed":
    #         succeed_count += 1
    #         count -= 1
    #
    #     print("\n")
    #     print("###########")
    #     print(buffer_mode, count)
    #     print("目前成功次数为%s，总次数为%s" % (succeed_count, i))
    #     print("###########\n")

    # 2.2 掉药
    drop.do(drop_info["box_matrix"], drop_info["num"])
    time.sleep(sleep_time)

    # 3、出药
    # 完成了全部取药过程，将药盒关盖并推出
    # lmr.push_out()
    # time.sleep(sleep_time)
    return


# 主函数循环
def main():
    # while True:
    #     continue
    # i = 0
    # while i < 50:
    #     strike.do(1)
    #     print(i)
    #     i += 1
    # print("打药结束")
    # print("2秒内可退出")
    # time.sleep(2)
    #
    # ============== 复位 ============
    reset = 0
    if reset:
        motor_reset.begin("fast")
        motor_reset.begin()                                   # 各轴到达传感器监测点
        reset = 0

    # # =========== 柜桶y基准测试 ===========
    # panel_standard.make_predict_model(1, 5)

    # ========= 大流程 ============
    i = 0
    while i < 1:
        video_introduction()
        i += 1
    print("1秒内可退出")
    time.sleep(2)

    # # go 测试
    # i = 0
    # while i < 50:
    #     i = i + 1
    #     go.only_z(0, 6.7, 10)
    #     print("暂停")
    #     time.sleep(0.1)
    #
    #     go.only_z(6.7, 10.5, 20)
    #     print("暂停")
    #     time.sleep(0.1)
    #
    #     go.only_z(10.5, 11.7, 15)
    #     print("暂停")
    #     time.sleep(0.1)
    #
    #     go.only_z(11.7, 10.5, 15)
    #     print("暂停")
    #     time.sleep(0.1)
    #
    #     go.only_z(10.5, 0)
    #     print("暂停")
    #     print(i)
    #     time.sleep(1.5)

    # 摇药部分测试
    # bottle.take_medicine(0, 0, 3)
    # time.sleep(1)

    # 测试取药
    # 黄连上清片
    # plate.do_take(6924168200093, 1, 5)
    # time.sleep(1)
    # plate.strike_drug_test(6924168200093, 1, [11, 9.85])
    # time.sleep(1)
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
    # plate.strike_drug_test(6921314097279, 1, [9.7, 10.4])
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
    # while True:
    #     strike.do(0.3)
    #     time.sleep(0.5)
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
