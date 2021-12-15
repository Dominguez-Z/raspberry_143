#!/usr/bin/env python 
# -*- coding:utf-8 -*-
import threading
from time import ctime, sleep


def music(func):
    for i in range(3):
        print("I was listening to %s.time is: %s" % (func, ctime()))
        sleep(5)
        # print("time is: %s" % ctime())


def movie(func):
    for i in range(3):
        print("I was at the %s!time is: %s" % (func, ctime()))
        sleep(2)


def x_move(distance):
    # 设定单位步长，由实际测了计算获知
    unit_step = 90 * 1e-3
    # 距离取绝对值再计算步数
    step_num_value = round(abs(distance) / unit_step)
    # 根据距离的正负确定运动方向
    if distance >= 0:
        direction = 'x_right'
    elif distance < 0:
        direction = 'x_left'
    else:
        print("函数需要指定方向和大小，正向右，负向左，单位毫米")
        return
    # 输出计算结果以便检测
    count_x = threading.activeCount()
    print("activeCount is : %s.time is: %s" % (count_x, ctime()))
    print("36：%s运动距离为：%s" % (direction, step_num_value))
    sleep(10)
    print("X.time is: %s" % ctime())


def y_move(distance):
    # 设定单位步长，由实际测了计算获知
    unit_step = 90.14 * 1e-3
    # 距离取绝对值再计算步数
    step_num_value = round(abs(distance) / unit_step)
    # 根据距离的正负确定运动方向
    if distance >= 0:
        direction = 'y_up'
    elif distance < 0:
        direction = 'y_down'
    else:
        print("函数需要指定方向和大小，正向右，负向左，单位毫米")
        return
    # 输出计算结果以便检测
    count_y = threading.activeCount()
    print("activeCount is : %s.time is: %s" % (count_y, ctime()))
    print("55：%s运动距离为：%s" % (direction, step_num_value))
    sleep(5)
    print("Y.time is: %s" % ctime())


def xy_go(coordinate_now, coordinate_target):
    x_distance = coordinate_target[0] - coordinate_now[0]
    y_distance = coordinate_target[1] - coordinate_now[1]

    threads = []
    t1 = threading.Thread(target=x_move, args=(x_distance,))
    threads.append(t1)
    t2 = threading.Thread(target=y_move, args=(y_distance,))
    threads.append(t2)
    for t in threads:
        t.setDaemon(True)
        t.start()
    for t in threads:
        t.join()
        print("threads : %s.time is: %s" % (t, ctime()))


def play():
    threads = []
    t1 = threading.Thread(target=music, args=(u'爱情买卖',))
    threads.append(t1)
    t2 = threading.Thread(target=movie, args=(u'变形金刚',))
    threads.append(t2)
    for t in threads:
        t.setDaemon(True)
        t.start()
    for t in threads:
        t.join()
        print("threads : %s.time is: %s" % (t, ctime()))


if __name__ == '__main__':
    xy_go([0, 0], [-200, 300])
    # play()
    count = threading.activeCount()
    # print("activeCount is : %s" % count)
    # while (count -1):
    #     count = threading.activeCount()
    #     print("activeCount is : %s" % count)
    print("activeCount is : %s\n all over.time is: %s" % (count, ctime()))
