# -*- coding: utf-8 -*-
"""
Created on Sun Dec 15 19:46:40 2019

@author: Jinfen Zhang
@edit by: Bruce
"""
import numpy as np
import math
from shapely.geometry import Polygon  #多边形

import LineCircleIntersection as lc
import GetArcPoints as ga

SCALE = 500           #速度的放大倍数，如果按最大速度画VO，则画的太小，所以需要放大
V_MAX = 20*1852/3600  #船舶的最大速度为20节，转换成m/s
ALPHA_MAX = 30        #船舶的最大转向角度为30°
DCPA = 500            #允许的最小会遇距离，单位是m


def GetVoPolygons(pos1,course1,speed1,pos2,course2,speed2):
    # 获得四个VO区域的多边形坐标集合
    
    # pos1为本船的位置向量，pos2为目标船位置向量
    # course1为本船的航向，course2为目标船航向，正北为0°，向右旋转为正
    # speed1为本船速度，speed2为目标船速度，m/s
    
    #返回的是shapely格式的polygon
    
    #船舶1的坐标
    pp1 = np.array(pos1)
    #船舶2速度向量终点坐标，起点为本船位置
    pp2 = np.array([pp1[0] + speed2 * np.sin(course2 * np.pi / 180) * SCALE,\
                    pp1[1] + speed2 * np.cos(course2 * np.pi / 180) * SCALE])
    
    #从pos1指向pos2的向量
    vec12 = np.array(pos2) - pp1
    #vec12逆时针旋转90°得到的向量
    vec12_rotate90 =  np.array([vec12[0] * np.cos(np.pi / 2) - vec12[1] * np.sin(np.pi / 2),\
                                vec12[0] * np.sin(np.pi / 2) + vec12[1] * np.cos(np.pi / 2)])
    pp4,pp3 = lc.LineCircleIntersection(pp1,V_MAX * SCALE, pp2, vec12_rotate90)
    
    gamma = math.asin(DCPA / np.linalg.norm(vec12)) * 180 / np.pi #安全角度
    #相对位置向量顺时针旋转gamma后的向量
    vec_rotate_right = [vec12[0] * np.cos(gamma * np.pi / 180) + vec12[1] * np.sin(gamma * np.pi / 180),\
                        -vec12[0] * np.sin(gamma * np.pi / 180) + vec12[1] * np.cos(gamma * np.pi / 180)]
    #相对位置向量顺时针旋转gamma后的向量
    vec_rotate_left = [vec12[0] * np.cos(gamma * np.pi / 180) - vec12[1] * np.sin(gamma * np.pi / 180),\
                       vec12[0] * np.sin(gamma * np.pi / 180) + vec12[1] * np.cos(gamma * np.pi / 180)]
    p_temp1, p_temp2 = lc.LineCircleIntersection(pp1,V_MAX * SCALE, pp2, vec_rotate_right)
    #这里还需要进一步判断
    vec1 = pp3 - pp1
    vec2 = p_temp1 - pp1
    if vec1[0] * vec2[1] - vec2[0] * vec1[1] > 0:
        pp5 = p_temp1
    else:
        pp5 = p_temp2
    
    p_temp1, p_temp2 = lc.LineCircleIntersection(pp1,V_MAX * SCALE, pp2, vec_rotate_left)
    #这里还需要进一步判断
    vec1 = p_temp1 - pp1
    vec2 = pp4 - pp1
    if vec1[0] * vec2[1] - vec2[0] * vec1[1] > 0:
        pp6 = p_temp1
    else:
        pp6 = p_temp2
    
    pp7 = np.array([pp1[0] + V_MAX * SCALE * np.sin((course1 + ALPHA_MAX) * np.pi / 180),\
                    pp1[1] + V_MAX * SCALE * np.cos((course1 + ALPHA_MAX) * np.pi / 180)])
    pp8 = np.array([pp1[0] + V_MAX * SCALE * np.sin((course1 - ALPHA_MAX) * np.pi / 180),\
                    pp1[1] + V_MAX * SCALE * np.cos((course1 - ALPHA_MAX) * np.pi / 180)])
    ##########################################################################
    #计算多个矩形区域
    # 1:整个速度向量区域
    point_temp = ga.GetArcPoints(pp1,pp7,pp8)
    poly_whole = np.vstack((pp1, pp7,point_temp,pp8)) #多个矩阵合并
    #python四边形对象，会自动生成逆时针的凸多边形
    poly_whole = Polygon(poly_whole).convex_hull
    
    #2：速度障碍区域
    point_temp = ga.GetArcPoints(pp1,pp5,pp6)
    poly_vo = np.vstack((pp2, pp5,point_temp,pp6)) #多个矩阵合并
    poly_vo = Polygon(poly_vo).convex_hull
    
    #3:poly_front
    point_temp = ga.GetArcPoints(pp1,pp6,pp4)
    poly_front = np.vstack((pp2, pp6,point_temp,pp4)) #多个矩阵合并
    poly_front = Polygon(poly_front).convex_hull
    
    #4:poly_rear
    point_temp = ga.GetArcPoints(pp1,pp3,pp5)
    poly_rear = np.vstack((pp2, pp3,point_temp,pp5)) #多个矩阵合并
    poly_rear = Polygon(poly_rear).convex_hull
    
    #5:poly_diverging
    point_temp = ga.GetArcPoints(pp1,pp4,pp3)
    poly_diverging = np.vstack((pp3,pp4,point_temp)) #多个矩阵合并
    poly_diverging = Polygon(poly_diverging).convex_hull
    
    ####################################################
    #求多个区域与poly_whole的相交区域
    if not poly_vo.intersects(poly_whole): #如果两四边形不相交
        poly_vo = []
    else:
        poly_vo        = poly_vo.intersection(poly_whole)
    
    if not poly_front.intersects(poly_whole): #如果两四边形不相交
        poly_front = []
    else:
        poly_front     = poly_front.intersection(poly_whole)
    
    if not poly_rear.intersects(poly_whole): #如果两四边形不相交
        poly_rear = []
    else:
        poly_rear      = poly_rear.intersection(poly_whole)
    
    if not poly_diverging.intersects(poly_whole): #如果两四边形不相交
        poly_diverging = []
    else:
        poly_diverging = poly_diverging.intersection(poly_whole)
    ##########################################################################    
    return poly_vo,poly_front,poly_rear,poly_diverging



#pos1 = [1000,-5134]
#course1 = 0
#speed1 = 5.144
#
#pos2 = [5446,2567]
#course2 = 240
#speed2 = 5.144
#
#poly_vo,poly_front,poly_rear,poly_diverging = GetVoPolygons(pos1,course1,speed1,pos2,course2,speed2)
#
#print(poly_vo)