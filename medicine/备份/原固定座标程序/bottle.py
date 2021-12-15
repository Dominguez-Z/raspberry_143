#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  bottle.py
#      Author:  钟东佐
#        Date:  2020/05/28
#    describe:  药瓶出药控制
#########################################################
import JSON.constant_coordinates as constant_coordinates
import JSON.coordinate_converter as coordinate_converter
import motor.go as go
import motor.y_drive as y
import motor.x_drive as x
import motor.z_drive as z
import motor.x1_drive as x1
import motor.y1_drive as y1
import time
import numpy as np

STEP_COUNT_MAX = 9          # 设定最大上升次数，限定转动角度
STEP_DISTANCE = 0.5         # 设定每步y轴上升0.5mm，约等于转动5度
STEP_PULSE_WIDTH = 3000     # 控制Y轴上升速度
TAKE_STEP_NUMBER = 20       # 能将药顶出来的上升


# ############################ 常数值设定区域 ############################
# push_out()
TAKE_MEDICINE_ANGLE_SLIP = -28          # 设定抬高出药口滑出药物时候的角度
TAKE_MEDICINE_TIME_SLIP = 0.7           # 设定出药延迟，使得药物有足够时间滑出至出药位
TAKE_MEDICINE_TIME_PUSH = 0.5           # 设定顶药后的延时

# push_out()、take_medicine()
TAKE_MEDICINE_ANGLE_PUSH_OUT = -33      # 设定降低出药口将药物顶出的角度

# take_medicine()
COUNT_CHECK_MAX = 4                     # 设定检查出药口准备药物情况的最大次数
BACK_MEDICINE_ANGLE = 40                # 设定回药的角度，使得药物回到瓶口附近但未回到瓶内
# ########################################################################


# ################################# 说明 #################################
# 用字典记录角度与坐标位置的关系，程序查询使用
# ########################################################################
# Y轴运动对应的角度
angle_y = {
    "90": 0,
    "85": 1.22,
    "80": 2.33,
    "75": 3.37,
    "70": 4.38,
    "65": 5.39,
    "60": 6.41,
    "55": 7.43,
    "50": 8.47,
    "45": 9.51,
    "40": 10.58,
    "35": 11.67,
    "30": 12.8,
    "25": 13.99,
    "20": 15.27,
    "15": 16.68,
    "10": 18.33,
    "5": 20.44,
    "0": 27.5
}
# Z轴运动对应的角度
angle_z = {
    "-0": 0,
    "-5": 0.96,
    "-10": 1.93,
    "-15": 2.93,
    "-20": 3.85,
    "-21": 4.04,
    "-22": 4.23,
    "-23": 4.42,
    "-24": 4.6,
    "-25": 4.79,
    "-26": 4.97,
    "-27": 5.16,
    "-28": 5.34,
    "-29": 5.52,
    "-30": 5.7,
    "-31": 5.88,
    "-32": 6.06,
    "-33": 6.26,
    "-35":6.7,
    "-40":7.7,
    "-45":8.7,
    "-50":9.7,
    "-55":10.7,
    "-60":11.7,
    "-65":12.7
}


# ############################### 函数说明 ###############################
# 指定轴转动到指定角度
# y轴坐标关注点是 推杆最前面
# z轴坐标关注点是 推杆上表面
# ########################################################################
# 1、正->正，只动y轴
def turn_y(angle):
    # 1、根据角度计算y轴目标坐标
    # 目标y坐标 = 准备点y坐标 + 目标角度对应偏移量
    target_y = ready_point[1] + angle_y.get(str(angle))
    # 2、获取当前y轴坐标
    the_front_body_push_rod = coordinate_converter.body_push_rod("the_front")
    # 3、执行y轴运动
    go.only_y(the_front_body_push_rod, target_y)
    time.sleep(0.1)
    # 4、更新目前角度
    global angle_current
    angle_current = angle
    # 5、运动结束，返回函数
    return


# 2、正->负，先动y轴，再动z轴
def turn_y_z(angle):
    # 1、先运动y轴到零度位置
    #   1.1 根据y轴零度角度计算y轴目标坐标
    #   目标y坐标 = 准备点y坐标 + y轴零度对应偏移量
    target_y = ready_point[1] + angle_y.get("0")
    #   1.2 获取当前y轴坐标
    the_front_body_push_rod = coordinate_converter.body_push_rod("the_front")
    #   1.3 执行y轴运动
    go.only_y(the_front_body_push_rod, target_y)
    time.sleep(0.1)

    # 2、再运动z轴到指定角度
    #   2.1 根据角度计算z轴目标坐标
    # 目标z坐标 = 准备点z坐标 + 目标角度对应偏移量
    target_z = ready_point[2] + angle_z.get(str(angle))
    #   2.2 获取当前z轴坐标
    the_top_body_push_rod = coordinate_converter.body_push_rod("the_top")
    #   2.3 执行z轴控制
    go.only_z(the_top_body_push_rod, target_z)
    time.sleep(0.1)

    # 3、更新目前角度
    global angle_current
    angle_current = angle

    # 4、完成控制，返回函数
    return


# 3、负->负，只动z轴
def turn_z(angle):
    # 1、根据角度计算z轴目标坐标
    # 目标z坐标 = 准备点z坐标 + 目标角度对应偏移量
    target_z = ready_point[2] + angle_z.get(str(angle))
    # 2、获取当前z轴坐标
    the_top_body_push_rod = coordinate_converter.body_push_rod("the_top")
    # 3、执行z轴控制
    go.only_z(the_top_body_push_rod, target_z)
    time.sleep(0.1)
    # 4、更新目前角度
    global angle_current
    angle_current = angle
    # 5、运动结束，返回函数
    return


# 4、负->正，先动z轴，再动y轴
def turn_z_y(angle):
    # 1、先运动z轴到零度位置
    #   1.1 根据z轴零度角度计算z轴目标坐标
    #   目标z坐标 = 准备点z坐标 + z轴零度对应偏移量
    target_z = ready_point[2] + angle_z.get("-0")
    #   1.2 获取当前z轴坐标
    the_top_body_push_rod = coordinate_converter.body_push_rod("the_top")
    #   1.3 执行y轴运动
    go.only_z(the_top_body_push_rod, target_z)
    time.sleep(0.1)

    # 2、再运动y轴到指定角度
    #   2.1 根据角度计算y轴目标坐标
    #   目标y坐标 = 准备点y坐标 + 目标角度对应偏移量
    target_y = ready_point[1] + angle_y.get(str(angle))
    #   2.2 获取当前y轴坐标
    the_front_body_push_rod = coordinate_converter.body_push_rod("the_front")
    #   2.3 执行y轴控制
    go.only_y(the_front_body_push_rod, target_y)
    time.sleep(0.1)

    # 3、更新目前角度
    global angle_current
    angle_current = angle

    # 4、完成控制，返回函数
    return


# ############################### 函数说明 ###############################
# 实现转动到指定角度
# ########################################################################
def turn_to(angle):
    # 1、判断输入的角度是否正确
    if (str(angle) not in angle_y) and (str(angle) not in angle_z):
        print("输入的角度不在程序记录的位置，请确定角度是否有误。")
        return

    # 2、根据目前角度和输入的角度对比执行需要的运动函数
    #   2.1 当前角度和目标角度都大于零，只动y轴
    if (angle_current >= 0) and (angle >= 0):
        print("只动y轴")
        turn_y(angle)
    #   2.2 当前角度和目标角度都小于零，只动z轴
    elif (angle_current <= 0) and (angle <= 0):
        print("只动z轴")
        turn_z(angle)
    #   2.3 当前角度大于零，目标角度小于零，先动y轴再动z轴
    elif (angle_current >= 0) and (angle <= 0):
        print("先动y轴再动z轴")
        turn_y_z(angle)
    #   2.4 当前角度小于零，目标角度大于零，先动z轴再动y轴
    elif (angle_current <= 0) and (angle >= 0):
        print("先动z轴再动y轴")
        turn_z_y(angle)
    else:
        print("判断旋转是否需要跨过水平线的程序出错，请检查bottle.py中的goto()")
        return

    """
        # 算法介绍：先判断目前角度和输入角度是否同号，再判断目前角度正负进而确定类型。
        # 如果同号，没有跨越水平线，只需要控制一个轴；
        if np.sign(angle_current) + np.sign(angle) != 0:
            # 如果当前角度为正，只需要控制y轴
            if np.sign(angle) > 0:
                turn_y(angle)
            # 如果当前角度为负，只需要控制z轴
            elif np.sign(angle) < 0:
                turn_z(angle)
        # 如果异号，跨越了水平线，需要先控制一个轴到达水平位置，再控制另一个轴。
        elif np.sign(angle_current) + np.sign(angle) == 0:
    """

    # 3、到达指定角度，函数返回
    return


# ############################### 函数说明 ###############################
# 当药片到达出口处，调用该函数实现出一粒药
# ########################################################################
def push_out():
    # 1、旋转加大角度使得出药口抬高，让出位置让药滑倒出药位
    turn_to(TAKE_MEDICINE_ANGLE_SLIP)
    time.sleep(TAKE_MEDICINE_TIME_SLIP)
    # 2、减小角度轴使得出药口下降，让顶针顶出药物
    turn_to(TAKE_MEDICINE_ANGLE_PUSH_OUT)
    time.sleep(TAKE_MEDICINE_TIME_PUSH)
    # 3、出一粒药完成，返回函数
    return


# ############################### 函数说明 ###############################
# 出药前检查是否有药准备好
# ########################################################################
def push_out_ready_check():
    # 目前是测试阶段，通过键盘输入 y/n 代替摄像头判断
    while True:
        # 1、接受输入 y/n
        ready_state = input("是否有药准备好出药，是：y；否：n。\n")
        if ready_state == 'y':
            return 'yes'
        elif ready_state == 'n':
            return 'no'
        else:
            print("输入有误，注意有药准备好了输入 y，否则输入 n")
            return 'error'


# ############################### 函数说明 ###############################
# 出药数量是否达到要求
# ########################################################################
def push_out_finish_check():
    # 目前是测试阶段，通过键盘输入 y/n 代替摄像头判断
    while True:
        # 1、接受输入 y/n
        finish_state = input("是否有出药，是：y；否：n。\n")
        if finish_state == 'y':
            num_medicine = int(input("成功出来的药物数量是多少，输入数字：\n"))
            return 'yes', num_medicine
        elif finish_state == 'n':
            return 'no', 0
        else:
            print("输入有误，注意出药数量准确输入 y，否则输入 n")


# ############################### 函数说明 ###############################
# 出药数量是否达到要求
# num_push_out 为需要出药数
# ########################################################################
def take_medicine(num_push_out):
    # 0、去到对应柜桶前处于准备状态
    turn_ready()
    # 1、初始化变量
    count_back_check = 0                        # 记录摇药循环次数
    count_push_out_check = 0                    # 记录出药循环次数
    num_push_out_succeed = 0                    # 记录成功出药个数
    # 2、 旋转到检查点
    turn_to(TAKE_MEDICINE_ANGLE_PUSH_OUT)
    
    # 3、进入摇药或出药循环
    while True:
        # 判断是否有药准备出
        ready_state = push_out_ready_check()
        
        # 3.1 如果没有药准备好，进入摇药循环
        if ready_state == "no":
            # 循环次数处理
            count_back_check += 1           # 摇药循环+1
            count_push_out_check = 0        # 出药循环置零
            # 判断检查次数是否超出最大值
            if count_back_check >= COUNT_CHECK_MAX:
                # 超出次数，旋转回90度并返回（失败，已出药个数）
                turn_to(90)
                return "fail", num_push_out_succeed
            elif 0 <= count_back_check < COUNT_CHECK_MAX:
                # 未超出次数，执行摇药动作
                turn_to(BACK_MEDICINE_ANGLE)                # 旋转到回到的位置
                turn_to(TAKE_MEDICINE_ANGLE_PUSH_OUT)       # 旋转到检查点
                continue                                    # 下一个循环
            else:
                print("判断检查次数count_check计算错误超出范围。")
                return "back_check_error", count_back_check
                
        # 3.2 如果有药准备好，进入出药循环
        elif ready_state == "yes":
            # 循环次数处理
            count_back_check = 0  # 摇药循环置零
            # 根据 接收到的颗粒数 - 成功出药数 循环执行出药动作
            for i in range(num_push_out - num_push_out_succeed):
                push_out()
            # 判断出药数量是否正确
            finish_state, num_medicine = push_out_finish_check()        # 接受状态和识别到的数量
            # 根据出药情况重置循环次数
            # 遇到成功出药就重置出药循环
            if finish_state == "yes":
                count_push_out_check = 0            # 出药循环次数置零
            # 出药检测不出药出药循环+1
            else:
                count_push_out_check += 1            # 出药循环次数+1
            num_push_out_succeed += num_medicine                      # 根据识别数量加到成功总数上
            
            # 判断1、成功出药数量符合指定数量
            if num_push_out_succeed == num_push_out:
                # 回到90度并返回成功
                turn_to(90)
                return "succeed", num_push_out_succeed
            
            # 判断2、成功出药数量未到指定数量
            elif 0 <= num_push_out_succeed < num_push_out:
                # 判断检查次数是否超出最大值
                # 超出次数
                if count_push_out_check >= COUNT_CHECK_MAX:
                    # 旋转回90度并返回（失败，已出药个数）
                    turn_to(90)
                    return "fail", num_push_out_succeed
                # 未超出次数，继续执行出药循环
                elif 0 <= count_push_out_check < COUNT_CHECK_MAX:
                    continue                                # 下一个循环
                # 
                else:
                    print("判断检查次数count_check计算错误超出范围。")
                    return "push_out_check_error", count_push_out_check
            
            # 判断3、成功出药数量出错
            else:
                print("成功出药数量不在 0~指定数量 之间。")
                return "num_push_out_succeed_error", num_push_out_succeed

        # 防止出错不知道
        else:
            print("准备状态变量ready_stare非“yes”或者“no”。")
            return "ready_state_error", ready_state


"""
# 以下为旧摇药动作
def take(ark_number=None):
    y_back_step = 0
    current_step_count = 0
    take_enabled = False
    target_coordinates_xyz = ark_barrels_coordinates.get(str(ark_number))           # 获取目标柜桶的坐标
    # 获取目前主体的坐标
    current_coordinates_body = coordinate_converter.body()
    # Z轴进入拿药位置
    # go.only_z(current_coordinates_body[2], target_coordinates_xyz[2])
    while current_step_count < STEP_COUNT_MAX:
        current_step_count += 1                                                     # 当前旋转次数计算
        print(current_step_count)
        y_distance = STEP_DISTANCE*step_wheel.get(str(current_step_count))          # 计算需要走的步数
        y_back_step += y.move(y_distance, STEP_PULSE_WIDTH)
        # y.move(-STEP_DISTANCE*1, STEP_PULSE_WIDTH)

        '''获取照片，分析照片'''
        time.sleep(1)
        if current_step_count == 9:
            take_enabled = True                                                    # 假设分析出可以出药

        if take_enabled:
            # take_step_number = TAKE_STEP_NUMBER                                   # 获取顶药的步数
            # 根据目前步数算出还要走的步数，并上升
            y_distance = (TAKE_STEP_NUMBER-count_wheel.get(str(current_step_count)))*STEP_DISTANCE
            y_back_step += y.move(y_distance, STEP_PULSE_WIDTH)
            time.sleep(2)
            y.move_step(-y_back_step, STEP_PULSE_WIDTH)                                  # 返回水平位置
            go.only_z(target_coordinates_xyz[2], current_coordinates_body[2])       # z轴退出拿药位置
            return 'take_success'
        else:
            pass
    y.move_step(-y_back_step, STEP_PULSE_WIDTH)                                         # 从最大位置返回水平
    # go.only_z(target_coordinates_xyz[2], current_coordinates_body[2])               # z轴退出拿药位置
    return 'take_not_success'
"""


# ############################### 函数说明 ###############################
# 做好摇药前的准备
# ########################################################################
def turn_ready():
    # 0、获取JSON文档中记录的准备点坐标
    global ready_point
    ready_point = constant_coordinates.get("bottle_turn", "ready_point")
    print(ready_point)
    # 1、取药夹打开到最大宽度，68;y1去到-60。机械位置需要
    go.only_x1(68)
    time.sleep(0.1)
    go.only_y1(-60)
    time.sleep(0.1)

    # 2、Z轴抬高至推杆前推完成可以使得转动装置水平状态的位置
    # 2.1 获取当前推杆上表面坐标
    the_top_body_push_rod = coordinate_converter.body_push_rod("the_top")
    # 2.2 获取推杆上表面目的坐标
    target_z = 307.6
    # 2.3 执行运动控制
    go.only_z(the_top_body_push_rod, target_z, 2000)
    time.sleep(0.1)

    # 3、推杆中心线对其转动装置传动位中心线
    # 3.1 获取当前推杆中心线坐标
    center_body_push_rod = coordinate_converter.body_push_rod("center")
    # 3.2 获取传动装置x方向中心线坐标
    x_center_transmission = 268.75
    # 3.3 执行x轴运动指令
    go.only_x(center_body_push_rod, x_center_transmission, 2000)
    time.sleep(0.1)

    # 4、推杆前进到前表面刚好接触传动装置
    # 4.1 获取当前推杆前表面坐标
    the_front_body_push_rod = coordinate_converter.body_push_rod("the_front")
    # 4.2 获取摇药装置垂直状态时，传动位y方向上最后的坐标
    target_y = 557
    # 4.3 执行y轴的控制
    go.only_y(the_front_body_push_rod, target_y, 1000)
    time.sleep(0.1)

    # 5、更新目前角度
    global angle_current
    angle_current = 90

    # 6、完成转动前的准备工作，更新函数返回
    return


# ############################### 函数说明 ###############################
# 转动到指定的角度
# ########################################################################
def rotate():
    # 1、测试转到水平，即y轴推到最前
    # 1.1 65度
    # goto(65)
    # time.sleep(1)
    # 1.2 45度
    turn_to(35)
    time.sleep(1)
    # 1.3 25度
    turn_to(-50)
    time.sleep(1)
    # 1.4 0度，水平
    # goto(0)
    # time.sleep(1)

    # 2、测试转到 -33度，即z轴上升到最高
    # 2.1 -15度
    # goto(-15)
    # time.sleep(1)
    # 2.2 -30度

    turn_to(-65)
    time.sleep(1)

    turn_to(35)
    time.sleep(1)

    turn_to(-50)
    time.sleep(1)

    turn_to(-65)
    time.sleep(1)

    turn_to(75)
    time.sleep(1)

    # 2.3 -33度，出药
    turn_to(90)
    time.sleep(1)

    # 3、完成指定转动角度工作，函数返回
    return


# 初始化设定
def setup():
    z_setup_return = z.setup()
    if not z_setup_return:
        print('Z轴初始化失败')

    x_setup_return = x.setup()
    if not x_setup_return:
        print('X轴初始化失败')

    y_setup_return = y.setup()
    if not y_setup_return:
        print('Y轴初始化失败')

    x1_setup_return = x1.setup()
    if not x1_setup_return:
        print('X1轴初始化失败')

    y1_setup_return = y1.setup()
    if not y1_setup_return:
        print('Y1轴初始化失败')

    return True


# 循环部分
def main():
    turn_ready()
    time.sleep(1)
    """
    state, num = take_medicine(5)
    print(state)
    print(num)
    """
    while True:
        # turn_to(-55)
        # time.sleep(1)

        turn_to(-65)
        time.sleep(1)

        turn_to(60)
        time.sleep(1)


    return


# 结束释放
def destroy():
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
