#!/usr/bin/env python 
# -*- coding:utf-8 -*-

import math
step_num = 99
pulse_width = 500

step_num_change_width = 1/10
pulse_width_max = 400
if pulse_width > pulse_width_max or pulse_width < 0:
    pulse_width = pulse_width_max

step_num_speedup = step_num * step_num_change_width
step_num_speeddown = step_num * (1 - step_num_change_width)
pulse_width_change = pulse_width_max - pulse_width
#print(pulse_width_change)
if step_num < 100:
    pulse_width_math = pulse_width
    for i in range(0, step_num):
        print(i, pulse_width_math)
else:
    for i in range(0, step_num):
        if i < step_num_speedup:
            x = math.pi * i / (step_num * step_num_change_width)
        elif step_num_speedup <= i < step_num_speeddown:
            x = math.pi
        elif step_num_speeddown <= i <= step_num:
            x = math.pi * (1 + (i - step_num_speeddown) / (step_num * step_num_change_width))

        A = (math.cos(x) + 1) / 2
        pulse_width_math = int(pulse_width_change * A + pulse_width)

