# -*- coding: utf-8 -*-
"""
Created on Sun Dec 15 19:44:14 2019

@author: Jinfen Zhang
@edit by: Bruce
"""
import numpy as np

# TODO: 进行BCD的转换

def LineCircleIntersection(circle_center,circle_radius, point_line, vec_line):
    #计算直线和圆的交点
    # circle_center为圆心坐标
    #circle_radius为圆的半径
    # point_line为直线的一个点
    # vec_line为直线的方向向量
    x_vec = vec_line[0]
    y_vec = vec_line[1]
    
    #将方向向量归一化
    vec_norm = np.linalg.norm(vec_line)
    x_vec /= vec_norm
    y_vec /= vec_norm
    
    x1 = circle_center[0]
    y1 = circle_center[1]
    
    x2 = point_line[0]
    y2 = point_line[1]
    
    lamda = ((x1 - x2) * x_vec + (y1 - y2) * y_vec) / (x_vec * x_vec + y_vec * y_vec)
    x_center,y_center = x2 + lamda * x_vec, y2 + lamda * y_vec
    
    R_2 = circle_radius ** 2
    r_2 = ((circle_center[0] - x_center) ** 2) + ((circle_center[1] - y_center) ** 2)
    dist = (R_2 - r_2) ** 0.5
    
    xx1 = x_center + x_vec * dist
    yy1 = y_center + y_vec * dist
    
    xx2 = x_center - x_vec * dist
    yy2 = y_center - y_vec * dist    
    
    #返回的第一个点是与直线向量方向相同的点，第二个点是与直线向量方向相反的点
    return np.array([xx1,yy1]), np.array([xx2,yy2])