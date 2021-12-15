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
import JSON.ark_barrels_coordinates as ark_barrels_coordinates
import JSON.params_correction as params_correction
import JSON.current_coordinates as current_coordinates
import motor.go as go
import motor.y_drive as y
import motor.x_drive as x
import motor.z_drive as z
import motor.x1_drive as x1
import motor.y1_drive as y1
import image.camera_0 as camera_0
import time
import numpy as np
import cv2


# ############################ 常数值设定区域 ############################
# push_out()
ANGLE_SLIP_BUFFER = [-30, -35, -40]         # 摇药设置缓冲角度，让药初步离开药瓶口
TAKE_MEDICINE_ANGLE_SLIP = -54              # 设定抬高出药口滑出药物时候的角度
TAKE_MEDICINE_TIME_SLIP_BUFFER = 0.5        # 设定出药缓冲延迟
TAKE_MEDICINE_TIME_SLIP = 0.7               # 设定出药延迟，使得药物有足够时间滑出至出药位
TAKE_MEDICINE_TIME_PUSH = 0.5               # 设定顶药后的延时
RPM_SLIP_BUFFER = [10, 10, 10]
RPM_SLIP = [16, 18, 20]

# push_out()、take_medicine()
TAKE_MEDICINE_ANGLE_PUSH_OUT = -54      # 设定降低出药口将药物顶出的角度
RPM_PUSH_OUT = 15

# take_medicine()
COUNT_CHECK_MAX = 3                     # 设定检查出药口准备药物情况的最大次数
BACK_MEDICINE_ANGLE = 65                # 设定回药的角度，使得药物回到瓶口附近但未回到瓶内
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
    "-35": 6.7,
    "-40": 7.7,
    "-42": 8.1,
    "-45": 8.7,
    "-50": 9.7,
    "-54": 10.5,
    "-55": 10.7,
    "-60": 11.7,
    "-65": 12.7
}


# ############################### 函数说明 ###############################
# 指定轴转动到指定角度
# y轴坐标关注点是 推杆最前面
# z轴坐标关注点是 推杆上表面
# ########################################################################
def turn_y(angle):
    """
    1、正->正，只动y轴

    Parameters
    ----------
    angle
        目标角度

    """
    global angle_current
    # 1、根据角度计算y轴目标坐标
    # 目标y坐标 = 准备点y坐标 + 目标角度对应偏移量
    target_y = ready_point[1] + angle_y.get(str(angle))
    # 2、获取当前y轴坐标
    the_front_body_push_rod = coordinate_converter.body_push_rod("the_front")
    # 3、执行y轴运动
    go.only_y(the_front_body_push_rod, target_y)
    time.sleep(0.1)
    # 4、更新目前角度
    angle_current = angle
    # 5、运动结束，返回函数
    return


def turn_y_z(angle, rpm_z=None):
    """
    2、正->负，先动y轴，再动z轴

    Parameters
    ----------
    angle
        目标角度
    rpm_z
        z轴移动速度，控制转动速度

    """
    global angle_current
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
    print("\n")
    print("############ y_z ############")
    print("准备点z坐标：%s，目标角度对应偏移量：%s" % \
          (ready_point[2], angle_z.get(str(angle))))
    print("z轴目前坐标：%s，目标坐标：%s。" % (the_top_body_push_rod, target_z))
    print("############ y_z ############")
    print("\n")
    go.only_z(the_top_body_push_rod, target_z, rpm_z)
    time.sleep(0.1)

    # 3、更新目前角度
    angle_current = angle

    # 4、完成控制，返回函数
    return


def turn_z(angle, rpm_z=None):
    """
    3、负->负，只动z轴

    Parameters
    ----------
    angle
        目标角度
    rpm_z
        z轴移动速度，控制转动速度

    """
    global angle_current
    # 1、根据角度计算z轴目标坐标
    # 目标z坐标 = 准备点z坐标 + 目标角度对应偏移量
    target_z = ready_point[2] + angle_z.get(str(angle))
    # 2、获取当前z轴坐标
    the_top_body_push_rod = coordinate_converter.body_push_rod("the_top")
    # 3、执行z轴控制
    print("\n")
    print("############ z ############")
    print("准备点z坐标：%s，目标角度对应偏移量：%s" % \
          (ready_point[2], angle_z.get(str(angle))))
    print("z轴目前坐标：%s，目标坐标：%s。" % (the_top_body_push_rod, target_z))
    print("############ z ############")
    print("\n")
    go.only_z(the_top_body_push_rod, target_z, rpm_z)
    time.sleep(0.1)
    # 4、更新目前角度
    angle_current = angle
    # 5、运动结束，返回函数
    return


def turn_z_y(angle):
    """
    4、负->正，先动z轴，再动y轴

    Parameters
    ----------
    angle
        目标角度

    """
    global angle_current
    # 1、先运动z轴到零度位置
    #   1.1 根据z轴零度角度计算z轴目标坐标
    #   目标z坐标 = 准备点z坐标 + z轴零度对应偏移量
    target_z = ready_point[2] + angle_z.get("-0")
    #   1.2 获取当前z轴坐标
    the_top_body_push_rod = coordinate_converter.body_push_rod("the_top")
    #   1.3 执行y轴运动
    print("\n")
    print("############ z_y ############")
    print("准备点z坐标：%s，目标角度对应偏移量：%s" % \
          (ready_point[2], angle_z.get("-0")))
    print("z轴目前坐标：%s，目标坐标：%s。" % (the_top_body_push_rod, target_z))
    print("############ z_y ############")
    print("\n")
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
    angle_current = angle

    # 4、完成控制，返回函数
    return


def turn_to(angle, rpm_z=None):
    """
    实现转动到指定角度

    Parameters
    ----------
    angle
        目标角度，范围是90到-60，出药管道水平设定为0度
    rpm_z
        z轴移动速度，控制转动速度,只有正->负，和负->负的时候可以指定，其他时候指定无效

    """
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
        turn_z(angle, rpm_z)
    #   2.3 当前角度大于零，目标角度小于零，先动y轴再动z轴
    elif (angle_current >= 0) and (angle <= 0):
        print("先动y轴再动z轴")
        turn_y_z(angle, rpm_z)
    #   2.4 当前角度小于零，目标角度大于零，先动z轴再动y轴
    elif (angle_current <= 0) and (angle >= 0):
        print("先动z轴再动y轴")
        turn_z_y(angle)
    else:
        print("判断旋转是否需要跨过水平线的程序出错，请检查bottle.py中的goto()")
        return

    # 3、到达指定角度，函数返回
    return


def push_out():
    """
    当药片到达出口处，调用该函数实现出一粒药
    并在顶出药的阶段拍照识别是否正常顶出

    Returns
    -------
    push_out_state - "succeed"，成功出药；"fail",出药不成功
    """

    # 1、减小角度轴使得出药口下降，让顶针顶出药物
    turn_to(TAKE_MEDICINE_ANGLE_PUSH_OUT, RPM_PUSH_OUT)
    time.sleep(TAKE_MEDICINE_TIME_PUSH)

    # 2、拍照识别
    # 拍照，并获取照片的绝对路径
    # picture_camera_path = camera_0.take_photo("push_out")
    # img = cv2.imread(picture_camera_path)
    # cv2.namedWindow("img1", cv2.WINDOW_NORMAL)
    # cv2.imshow("img1", img)
    # img = img[720:820, 690:700]
    # gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # ret, thresh = cv2.threshold(gray_image, 220, 255, cv2.THRESH_BINARY_INV)
    #
    # binary, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # i = len(contours)
    # cv2.imshow("img2", img)
    # cv2.imshow("gray_image", gray_image)
    # cv2.imshow("thresh", thresh)
    # cv2.waitKey(0)
    #
    # cv2.destroyAllWindows()
    # print("push_out识别结果，i = %s" % i)
    # time.sleep(TAKE_MEDICINE_TIME_PUSH)

    # 默认有就能出
    i = 1

    # 3、旋转加大角度使得出药口抬高，让出位置让药滑倒出药位
    turn_to(TAKE_MEDICINE_ANGLE_SLIP, RPM_PUSH_OUT)
    time.sleep(TAKE_MEDICINE_TIME_SLIP)

    # 4、根据识别结果，返回状态
    if i == 1:
        return "succeed"
    else:
        return 'fail'


def push_out_ready_check():
    """
    出药前检查是否有药准备好

    Returns
    -------
    Return
        "yes"-有药，
        "no"-无药，
        "error"-判断出错。
    """
    # 拍照，并获取照片的绝对路径
    picture_camera_path = camera_0.take_photo(picture_name="push_out_ready_check",
                                              focus_absolute=camera_0.FOCUS_ABSOLUTE_BOTTLE)
    picture_dir_path = picture_camera_path.replace("push_out_ready_check.jpg", "", 1)
    print(picture_dir_path)
    img = cv2.imread(picture_camera_path)
    # cv2.namedWindow("img1", cv2.WINDOW_NORMAL)
    # cv2.imshow("img1", img)
    img = img[735:788, 603:613]
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray_image, 220, 255, cv2.THRESH_BINARY_INV)

    binary, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    i = len(contours)
    # cv2.imshow("img2", img)
    # cv2.imshow("gray_image", gray_image)
    # cv2.imshow("thresh", thresh)

    cv2.imwrite(picture_dir_path + "gray_image.jpg", gray_image)
    cv2.imwrite(picture_dir_path + "thresh.jpg", thresh)
    # cv2.waitKey(0)

    # cv2.destroyAllWindows()
    print("push_out_ready_check识别结果，i = %s" % i)
    if i == 2:
        return 'yes'
    else:
        return 'no'
    # elif i == 1:
    #     return 'no'
    # else:
    #     print("图像识别有误")
    #     return 'error'


def turn_to_ready_check(mode=None):
    """
    摇药出来的动作，依据指定的不同模式进行不同控制

    Parameters
    ----------
    mode
        模式，SLIP_BUFFER的角度根据瓶内药的数量分为4个级别。
        数量越多，药越满，角度越小。
        SLIP_BUFFER[0]角度最小，[2]最大

    """
    turn_to(ANGLE_SLIP_BUFFER[mode], RPM_SLIP_BUFFER[mode])
    time.sleep(TAKE_MEDICINE_TIME_SLIP_BUFFER)
    turn_to(TAKE_MEDICINE_ANGLE_SLIP, RPM_SLIP[mode])
    time.sleep(TAKE_MEDICINE_TIME_SLIP)
    return


def take_medicine(row, line, num_push_out, mode=3):
    """
    实现去到指定柜桶取出指定数量的药丸

    Parameters
    ----------
    row
        柜桶所在的行，0开始
    line
        柜桶所在的列，0开始
        例如：4行5列，key = "3-4"
    num_push_out
        需要取出的药丸数量
    mode
        模式，SLIP_BUFFER的角度根据瓶内药的数量分为4个级别。
        数量越多，药越满，角度越小。
        SLIP_BUFFER[0]角度最小，[2]最大

    Returns
    -------
    return
        "push_out_check_error", count_push_out_check -
        判断检查次数count_check计算错误超出范围。
        "num_push_out_succeed_error", num_push_out_succeed -
        成功出药数量不在 0~指定数量 之间。
        "ready_state_error", ready_state -
        准备状态变量ready_stare非“yes”或者“no”。
    """
    sleep_time = 0.1  # 动作运动间隔的时间

    # 0、去到对应柜桶前处于准备状态
    turn_ready(row, line)
    time.sleep(sleep_time)
    # 1、初始化变量
    count_back_check = 0                        # 记录摇药循环次数
    count_push_out_check = 0                    # 记录出药循环次数
    num_push_out_succeed = 0                    # 记录成功出药个数
    # 2、 旋转到检查点
    turn_to_ready_check(mode)
    
    # 3、进入摇药或出药循环
    while True:
        # 判断是否有药准备出
        time.sleep(sleep_time)
        ready_state = push_out_ready_check()
        time.sleep(sleep_time)
        
        # 3.1 如果没有药准备好，进入摇药循环
        if ready_state == "no":
            # 循环次数处理
            count_back_check += 1           # 摇药循环+1
            print("\n###########")
            print(count_back_check)
            print("\n##########")
            count_push_out_check = 0        # 出药循环置零
            # 判断检查次数是否超出最大值
            if count_back_check >= COUNT_CHECK_MAX:
                # 超出次数，旋转回90度并返回（失败，已出药个数）
                finish_back()
                return "fail", num_push_out_succeed
            elif 0 <= count_back_check < COUNT_CHECK_MAX:
                # 未超出次数，执行摇药动作
                turn_to(BACK_MEDICINE_ANGLE)                # 旋转到回药的位置
                print("\n")
                print("\n")
                print(count_back_check)
                print("\n")
                print("\n")
                time.sleep(0.5)
                turn_to_ready_check(mode)                   # 旋转到检查点
                continue                                    # 下一个循环
            else:
                print("判断检查次数count_check计算错误超出范围。")
                finish_back()
                return "back_check_error", count_back_check
                
        # 3.2 如果有药准备好，进入出药循环
        elif ready_state == "yes":
            # 循环次数处理
            count_back_check = 0  # 摇药循环置零
            # 进行出药动作，并接受出药状态
            ready_state = push_out()
            time.sleep(sleep_time)

            # 根据出药情况重置循环次数
            # 遇到成功出药就重置出药循环
            if ready_state == "succeed":
                count_push_out_check = 0            # 出药循环次数置零
                num_push_out_succeed += 1           # 成功出药数+1
            # 出药检测不出药出药循环+1
            else:
                count_push_out_check += 1            # 出药循环次数+1

            # 判断1、成功出药数量符合指定数量
            if num_push_out_succeed == num_push_out:
                # 回到90度并返回成功
                finish_back()
                return "succeed", num_push_out_succeed
            
            # 判断2、成功出药数量未到指定数量
            elif 0 <= num_push_out_succeed < num_push_out:
                # 判断检查次数是否超出最大值
                # 超出次数
                if count_push_out_check >= COUNT_CHECK_MAX:
                    # 旋转回90度并返回（失败，已出药个数）
                    finish_back()
                    return "fail", num_push_out_succeed
                # 未超出次数，继续执行出药循环
                elif 0 <= count_push_out_check < COUNT_CHECK_MAX:
                    continue                                # 下一个循环
                # 
                else:
                    print("判断检查次数count_check计算错误超出范围。")
                    finish_back()
                    return "push_out_check_error", count_push_out_check
            
            # 判断3、成功出药数量出错
            else:
                print("成功出药数量不在 0~指定数量 之间。")
                finish_back()
                return "num_push_out_succeed_error", num_push_out_succeed

        # 防止出错不知道
        else:
            print("准备状态变量ready_stare非“yes”或者“no”。")
            finish_back()
            return "ready_state_error", ready_state


def finish_back():
    """
    摇药过程中任何情况结束时，函数退出前调用，保证推杆离开摇药位置，
    处于xz轴运动，y方向是安全的状态，避免碰撞

    """
    # 先转回90度的位置
    turn_to(90)
    # y后退到安全位置，保证xz运动安全，防撞
    go.xz_move_y_safe()
    time.sleep(0.1)
    return


def turn_ready(row, line):
    """
    做好摇药前的准备，该函数关注点仍然是坐标，后续摇药的控制将变为关注角度

    Parameters
    ----------
    row
        柜桶所在的行，0开始
    line
        柜桶所在的列，0开始
        例如：4行5列，key = "3-4"

    Raises
    ------
    ready_point
        [x, y, z]，记录了准备点后，目前各轴关注点的坐标，用于后续角度转化为运动距离后的基准。
        目前是全局变量，后续可以通过返回传参保证代码的稳定。
    angle_current
        当前角度，用于判断运动是否需要y轴和z轴协同控制。
        目前是全局变量，后续可以通过返回传参保证代码的稳定。
    """
    # 1、数据准备
    # 1.1 创建一个全局列表，记录准备点坐标[x, y, z]
    global ready_point
    ready_point = [0, 0, 0]
    sleep_time = 0.1                    # 动作运动间隔的时间
    # 1.2 指定药柜的修正参数
    params_correction_xyz = params_correction.get_ark_barrels(row, line)
    # 1.3 指定药柜的传动装置坐标
    ark_barrels_xyz = ark_barrels_coordinates.get_bottle(row, line)

    # 2、x1轴和y1轴调整
    # 2.1 取药夹打开到最大宽度，68
    go.only_x1(68)
    time.sleep(sleep_time)
    # 2.2 y1轴，夹具前表面缩进相距 药板支撑平台y向前表面 -65的位置
    y1_now1 = coordinate_converter.body_tong("the_front_y")
    y1_target1 = coordinate_converter.body("the_front_supporting_parts") - 65
    go.only_y1(y1_now1, y1_target1)
    time.sleep(sleep_time)

    # xz平面运动前提是y方向不会碰撞
    # 使用了go.xz，因此可以不需要了
    # go.xz_move_y_safe()
    # time.sleep(sleep_time)

    # 3、Z轴抬高至推杆前推完成可以使得转动装置水平状态的位置
    # 4、推杆中心线对其转动装置传动位中心线

    # 3.1 获取当前推杆上表面坐标
    the_top_body_push_rod = coordinate_converter.body_push_rod("the_top")
    # 3.2 获取转动装置呈水平状态时，与推杆上表面的接触面坐标
    # 需要加上误差修正参数
    z_target1 = ark_barrels_xyz[2] + params_correction_xyz[2]
    # 4.1 获取当前推杆中心线坐标
    center_body_push_rod = coordinate_converter.body_push_rod("center")
    # 4.2 获取传动装置x方向中心线坐标
    # 需要加上误差修正参数
    x_target1 = ark_barrels_xyz[0] + params_correction_xyz[0]

    # 3.3 执行运动控制
    # go.only_z(the_top_body_push_rod, z_target1)
    # 4.3 执行x轴运动指令
    # go.only_x(center_body_push_rod, x_target1)
    go.xz(coordinate_now_x=center_body_push_rod,
          coordinate_target_x=x_target1,
          coordinate_now_z=the_top_body_push_rod,
          coordinate_target_z=z_target1)

    # 3.4 更新ready_point
    ready_point[2] = coordinate_converter.body_push_rod("the_top")
    time.sleep(sleep_time)
    # 4.4 更新ready_point
    ready_point[0] = x_target1
    time.sleep(sleep_time)

    # 5、推杆前进到前表面刚好接触传动装置
    # 5.1 获取当前推杆前表面坐标
    the_front_body_push_rod = coordinate_converter.body_push_rod("the_front")
    # 5.2 获取摇药装置垂直状态时，传动位y方向上最后的坐标
    # 需要加上误差修正参数
    y_target1 = ark_barrels_xyz[1] + params_correction_xyz[1]
    # 5.3 执行y轴的控制
    go.only_y(the_front_body_push_rod, y_target1)
    # 5.4 更新ready_point
    ready_point[1] = coordinate_converter.body_push_rod("the_front")
    time.sleep(0.1)

    # 6、更新目前角度
    global angle_current
    angle_current = 90

    # 7、完成转动前的准备工作，更新函数返回
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
    # # 2.1 摇药
    sleep_time = 0
    i = 0
    succeed_count = 0
    sum = 200
    count = 104
    while i < 50:
        i += 1
        buffer_mode = int(2 - (count // ((sum + 3)//3)))
        state, num = take_medicine(0, 1, 1, mode=buffer_mode)
        time.sleep(sleep_time)
        if state is "succeed":
            succeed_count += 1
            count -= 1
        print("\n")
        print("###########")
        print(buffer_mode, count)
        print("目前成功次数为%s，总次数为%s" % (succeed_count, i))
        print("###########\n")

    # camera_0.take_photo(picture_name="push_out_ready_check_focus",
    #                     focus_absolute=camera_0.FOCUS_ABSOLUTE_BOTTLE)
    # turn_ready(0, 0)
    # time.sleep(1)
    """
    state, num = take_medicine(5)
    print(state)
    print(num)
    """
    # while True:
    #     # turn_to(-55)
    #     # time.sleep(1)
    #
    #     turn_to(-65)
    #     time.sleep(1)
    #
    #     turn_to(60)
    #     time.sleep(1)


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
