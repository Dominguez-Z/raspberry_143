#!/usr/bin/env python 
# -*- coding:utf-8 -*-


def setup():
    """
    初始化设定
    """

    return True


def main():
    """
    主函数
    """
    while True:
        return


def destroy():
    """
    结束释放
    """
    return


if __name__ == '__main__':  # 程序从这开始
    """
    如果该程序为主程序，程序在此开始运行，若不是不运行，该文件只做函数定义
    """
    # 初始化
    setup_return = setup()
    if setup_return:
        print('始化成功')

    try:
        main()
    except KeyboardInterrupt:  # 当按下 'Ctrl+C', 子函数 destroy()将会运行，用于停止退出
        print("程序已停止退出...")
        destroy()
 