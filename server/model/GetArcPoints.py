# -*- coding: utf-8 -*-
"""
Created on Sun Dec 15 19:45:43 2019

@author: Jinfen Zhang
@edit by Bruce
"""
import numpy as np
import math

def GetArcPoints(center_point,start_point,end_point):
    # center_point是圆弧的圆心坐标
    # start_point是圆弧的起点坐标
    # end_point是圆弧的终点坐标
    # 求从start_point逆时针旋转到end_point的圆弧点集
    first_arc = start_point - center_point
    end_arc = end_point - center_point
    
    r_arc = np.linalg.norm(first_arc) #圆弧半径
    # 弧的圆心角，°
    theta_arc = math.acos(np.dot(first_arc,end_arc)/(r_arc ** 2)) * 180 / np.pi
    
    points = start_point
    for theta in np.arange(1,theta_arc,1):
        #旋转角度
        theta_rotate = np.array([[np.cos(theta * np.pi / 180), -np.sin(theta * np.pi / 180)],\
                                 [np.sin(theta * np.pi / 180), np.cos(theta * np.pi / 180)]])
        p_temp = center_point + np.dot(theta_rotate,first_arc)
        points = np.vstack((points, p_temp)) #两个矩阵合并
    
    return points