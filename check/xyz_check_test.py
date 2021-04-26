#!/usr/bin/env python 
# -*- coding:utf-8 -*-
#########################################################
#   File name:  xyz_check_test.py
#      Author:  钟东佐
#        Date:  2020/5/13
#    describe:  用于测试
#########################################################

import json
ARK_BARRELS_FILE_PATH = '../JSON/ark_barrels_coordinates.json'
CURRENT_COORDINATES_FILE_PATH = '../JSON/current_coordinates.json'

f = open(CURRENT_COORDINATES_FILE_PATH)
current_coordinates = json.load(f)
f.close()
x = [2,4,5]
print(current_coordinates['body_xyz'])
current_coordinates['body_xyz'] = x
print(current_coordinates['body_xyz'])
f = open(CURRENT_COORDINATES_FILE_PATH, 'w')
json.dump(current_coordinates, f, indent=4)
f.close()

# print(current_coordinates_xyz)
