""" create VM
VM 运行一步
对每个船：
    如果领域内有船：
        算DCPA(金奋)->算法1
        p = exp{DCPA . *}
        如果 p>0.8:
            做决策，多船决策算法 ->算法2
            返回决策内容
        状态不变，返回空的决策结果
    状态不变，返回空的决策结果
如果有船做决策：
    分支
否则：
    状态不变

决策内容：
1. 每艘船的决策状态[F, F, F ,T]
2. 每艘船的决策内容[[],[], [], [***]]
3. 每艘船的状态，位置 """


# 修正：
""" 
create VM
VM 运行一步
对每个船：
    如果已经做了决策：
        决策没执行完：
            按决策走
        否则：
            回正状态，走一步
    否则：
        如果领域内有船：
            对雷达范围内的每一个船：
                DCPA: 
            p = exp{DCPA . *}
            如果 p>0.8:
                做决策，多船决策算法->算法2
                返回决策内容
            状态不变，返回空的决策结果
        状态不变，返回空的决策结果
如果有没做决策的船 新做了决策：
    分支
否则：
    状态不变 
"""


多船决策算法->算法2
输入：本船和雷达范围内的目标船 状态
判断目标船是直航or让路 
我是让路
对每一艘直航船：
    夹角<22.5?
        将其纳入小角度集合{GW1}
    否则：
        纳入大角度集合{GW2}
返回{GW1}, {GW2}

对{GW1}中的每一个：
    计算我船和他的决策结果（减速阶段）
    返回最严格的结果 记作{R1}

对{GW2}中的每一个：
    以{R1}作为初始状态，计算决策结果(转向阶段)
    返回最严格的结果 记作{R2}

{R2}就是多船决策的结果


决策内容：
1. 每艘船的决策状态[F, F, F ,T]
2. 每艘船的决策内容[[],[], [], [***]]
3. 每艘船的状态，位置 

本船在新航线上走的总时间 记作tc1

目标船已经在新航线上航行时间 记作 t2new
目标船在新航线走的总时间 记作 tc2
若目标船未决策 则 t2new, tc2 = 0
目标船决策的内容 新的速度 v2new, 新的角度 a2new


算法1 JDCPA
输入：pos1, a1, v1, pos2, a2, v2, tc1, v1new, a1new, t2new, tc2, a2new, v2new
如果目标船未决策：
    D0 = DynamicDCPA(pos1, a1, v1, pos2, a2, v2, tc1, v1new)
    D0 = DynamicDCPA(pos1, a1_temp, v1, pos2, a2, v2, tc1, v1new)
否则：
    tc1 > (tc2-t2new)?:
        # 对方先回正
        D1 = DCPA(pos1, a1new, v1new, pos2, a2new, v2new)
        pos2new = 按照 tc2-t2new 更新
        D2 = DCPA(pos1, a1new, v1new, pos2new, a2, v2)
        pos1new = 按照 tc1 更新
        D3 = DCPA(pos1new, a1, v1, pos2new, a2, v2)
        返回min(D1, D2, D3)
    否则：
        D1 = DCPA(pos1, a1new, v1new, pos2, a2new, v2new)
        pos1new = 按照 tc1 更新
        D2 = DCPA(pos1new, a1, v1, pos2, a2new, v2new)
        pos2new = 按照 tc2-t2new 更新
        D3 = DCPA(pos1new, a1, v1, pos2new, a2, v2)
        返回min(D1, D2, D3)
min(D0, min(D1, D2, D3))




