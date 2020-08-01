#-------------------------------------------------------------------------------
# Name:        SimVM
# Purpose:     实现一个线程安全仿真环境，其中包含多条自主航行船舶、观测者、环境数据
#
# Author:      Youan
# Helper:      Bruce
# Created:     27-01-2020
# Copyright:   (c) Youan 2020
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import sys
sys.path.append(".")
sys.path.append("..")
import math, random, time, copy, uuid, threading
import TransBCD, DrawVoAreas, opt_db, CPA
import HumanActivity as HA
import CreateEncounterSituation

class SimShip:
    # 仿真船舶决策类，实现一步决策
    def __init__(self, SimVMID, ShipID, SVM, Tick = 0, Lon = 0.0, Lat = 0.0, Speed = 0.0, Heading = 0.0, TimeRatio = 10, ):
        # super().__init__(self, SimShipRegistered)
        self.VMid     = SimVMID   # 所属虚拟机
        self.id       = ShipID    #船舶的ID号码
        self.lon      = Lon       #船舶经度坐标
        self.lat      = Lat       #船舶纬度坐标
        self.speed    = Speed     #船舶速度,m/s
        self.heading  = Heading   #船艏向，°，正北方向为 0，顺时针旋转为正
        self.interval = TimeRatio #一次离散步长所对应的时间间隔
        self.tick     = Tick      #当前虚拟时钟
        self.VOImgID = None
        self.DCPA  =  999999
        self.TCPA = 999999
        self.simVM = SVM
        self.instructions_queue = []
        self.old_speed = Speed
        self.old_heading = Heading
        self.dis = 999999
        self.mtc = 0
        # self.instructions_status
        pass
    
    # def get_recorder(self):
    #     return {
    #         'speed': self.speed, 
    #         'heading': self.heading,
    #     }

    def update_tick(self):
        self.tick += self.interval

    def instructions_mapping(self, instruction_code):
        # 指令映射，将不同的指令映射为不同的操作函数
        # mapping = {
        #     '1001': self.turn_left(),
        #     '1002': self.turn_right(),
        #     '2001': self.go_ahead()
        # }
        # return mapping.get(str(instruction_code))
        if instruction_code == 1001:
            return self.turn_left()
        elif instruction_code == 1002:
            return self.turn_right()
        else:
            return self.go_ahead()

    def turn_left(self):
        self.heading -= 5
    
    def turn_right(self):
        self.heading += 5
    
    def go_ahead(self):
        distance = self.speed * self.interval # 单位为米
        # xx = self.lon + distance * math.sin(math.radians(self.heading))
        # yy = self.lat + distance * math.cos(math.radians(self.heading))
        # print('!!!: heading: ', self.heading)
        # if type(self.heading) == tuple:
        #     heading = int(self.heading[0])
        # else:
        #     heading = int(self.heading)
        # print("heading, type of heading, distance, type of distance: ",heading, type(heading), distance, type(distance))
        x_com = distance * math.sin(math.radians(self.heading))
        y_com = distance * math.cos(math.radians(self.heading))
        xx = TransBCD.DeltaMeter2DeltaLon(x_com, self.lat)
        yy = TransBCD.DeltaMeter2DeltaLat(y_com)
        self.lon += xx
        self.lat += yy
        print('已前进，当前位置', self.lon, self.lat)

    def parse_decition(self, mtc, ma, mv):
        # 解析决策将决策转化为指令
        # 无人船决策结果为 tc, alpha, v1new
        # TODO 注意 这里还没有恢复原始状态
        # mtc, ma, mv = HA.A1(10, 9.8, [123, 35], 350, 10.2, [123.1, 35])
        da = 5
        ins = []
        if ma == 0:
            if mtc == 0:
                self.execute_instruction = ins
                # 未作出决策
                pass
            else:
                # 处于减速的情况 # e.g. mtc, ma, mv = 3, 0, 10
                t = int(mtc/self.interval) # 运行步数, 以mv的速度运行t步
                self.SetSpeed(mv)
                for i in range(t):
                    ins.append([2001])
                self.instructions_queue = ins
                # TODO 决策执行完之后怎么恢复原始速度 这个应该在执行决策的地方处理
        else:
            # 处于之间减速到指定值，再转弯后再前行一定步数的情况 e.g. mtc, ma, mv = 30, 15, 10
            if ma > 0:
                # 右转
                k = int(ma/da)
                ki = []
                for i in range(k):
                    ki.append(1002)
                ki.append(2001)
                ins.append(ki)
                t = int(mtc/self.interval)
                for j in range(t-1):
                    ins.append([2001])
                self.instructions_queue = ins
            else:
                # 左转
                k = int(ma/-da)
                ki = []
                for i in range(k):
                    ki.append(1001)
                ki.append(2001)
                ins.append(ki)
                t = int(mtc/self.interval)
                for j in range(t-1):
                    ins.append([2001])
                self.instructions_queue = ins
                pass

    def execute_instruction(self):
        ins = self.instructions_queue
        if len(ins) > 0:
            # 当前还处在执行决策阶段 指令还没执行完毕
            this_ins = ins[0]
            for step in this_ins:
                self.instructions_mapping(step)
            self.instructions_queue = ins[1:] #更新
            self.mtc -= 10
            if self.mtc <= 0:
                self.heading = self.old_heading
                self.speed = self.old_speed
        else:
            # TODO 未作出决策 或者说决策的内容为空 或者决策指令已经执行完毕
            self.go_ahead()


    def update_dis(self):
        if self.id == '10086':
            that_ship = self.simVM.SimShipRegistered[1]
        else:
            that_ship = self.simVM.SimShipRegistered[0]
        self.dis = math.sqrt((self.lon - that_ship.lon) ** 2 + (self.lat - that_ship.lat) ** 2)

    def confirm_status(self):
        # 确认状态-> (记录状态-> 决策-> 解析决策结果->) 执行指令
        if self.id == '10086':
            that_ship = self.simVM.SimShipRegistered[1]
        else:
            that_ship = self.simVM.SimShipRegistered[0]

        if len(self.instructions_queue) == 0:
            # self.recorder = self.get_recorder()
            # that_ship = self.simVM.SimShipRegistered[1]
            pos2, heading2, speed2 = [that_ship.lon, that_ship.lat], that_ship.heading, that_ship.speed
            # mtc, ma, mv = HA.HLD(10, 9.8, [123, 35], 350, 10.2, [123.1, 35])
            mtc, ma, mv = HA.HLD(self.heading, self.speed, [self.lon, self.lat], heading2, speed2, pos2)
            print('ship {} mtc, ma, mv: '.format(self.id), mtc, ma, mv)
            self.mtc -= mtc
            self.parse_decition(mtc, ma, mv)
            self.execute_instruction()
        else:
            self.execute_instruction()

    def update_cpa(self):
        if self.id == '10086':
            that_ship = self.simVM.SimShipRegistered[1]
        else:
            that_ship = self.simVM.SimShipRegistered[0]
        pos2, heading2, speed2 = [that_ship.lon, that_ship.lat], that_ship.heading, that_ship.speed
        DCPA = CPA.ComputeDCPA([self.lon, self.lat], self.heading, self.speed, pos2, heading2, speed2)
        TCPA = CPA.ComputeTCPA([self.lon, self.lat], self.heading, self.speed, pos2, heading2, speed2)
        self.DCPA = DCPA
        self.TCPA = TCPA
    
    def calc_prob(self):
        p = math.exp(self.DCPA * 1.05 * (-1) / 1000)
        return p
        
    def RunOneStep(self):
        if self.id == '10086':
            self.update_dis()
            if self.dis > 0.05:
                self.go_ahead()
                print('current distance:', self.dis)
                return 0
            else: 
                self.update_cpa()
                # if self.TCPA > 1500:
                if True:
                    if self.mtc >= 0:
                        p = self.calc_prob()
                        if p > 0.16:
                            self.confirm_status()
                        else:
                            self.execute_instruction()
                        # 尚未汇遇
                        return 0
                    else:
                        # self.speed = self.old_speed
                        # self.heading = self.old_heading
                        self.execute_instruction()
                        return 0
                else:
                    # 已汇遇
                    # self.update_status()
                    return 1 # 汇遇停
                    # return 0 # 汇遇不停
        else:
            self.go_ahead()
            return 0


    def SyncClock(self, simVM):
        simVM.SysClock = self.tick
        pass

    def RunOneDecision(self, RunFlag):
        if self.id == '10086': # 目前只有主船决策
            if RunFlag == 2:
                self.DecitionCore(self.__TurnLeft)
                # print('\nFlag2 This Ship.time: ', self.tick)
                # TODO: 之后是否要修正方向, 当前在转行函数中自动修正
            elif RunFlag == 3:
                self.DecitionCore(self.__TurnRight)
                # TODO: 之后是否要修正方向, 当前在转行函数中自动修正
            else:
                self.DecitionCore(self.__RunOneStep)
        else:
            self.DecitionCore(self.__RunOneStep)
            pass

    def GetShipStatus(self):
        shipStatus = {} # 创建一个空字典
        shipStatus['time'] = self.tick
        shipStatus['VMid'] = self.VMid
        shipStatus['shipid'] = self.id
        shipStatus['lon'] = self.lon
        shipStatus['lat'] = self.lat
        shipStatus['speed'] = self.speed
        shipStatus['heading'] = self.heading
        shipStatus['interval'] = self.interval
        shipStatus['VOImgID'] = self.VOImgID
        shipStatus['DCPA'] = self.DCPA
        shipStatus['TCPA']  = self.TCPA
        return shipStatus

    def Turn(self, delta_course=5):
        # 调整角度, delta_course>0:右转, delta_course<0:左转.
        self.heading = self.heading + delta_course

    def Go(self):
        # 简单计算，详细有待航海学相关内容
        # lon, lat: 起始坐标
        # speed: 航速，待统一转换，初步单位为 m/s
        # heading: 航向角，以正北为基准顺时针度量到航向线的角度
        # distance：本周期内，船舶行走的距离长度，初步单位为米
        # math.radians()将角度转换为弧度
        # 返回值：新的坐标点
        distance = self.speed * self.interval # 单位为米
        # xx = self.lon + distance * math.sin(math.radians(self.heading))
        # yy = self.lat + distance * math.cos(math.radians(self.heading))

        x_com = distance * math.sin(math.radians(self.heading))
        y_com = distance * math.cos(math.radians(self.heading))
        xx = TransBCD.DeltaMeter2DeltaLon(x_com, self.lat)
        yy = TransBCD.DeltaMeter2DeltaLat(y_com)
        x = self.lon + xx
        y = self.lat + yy

        # heading, speed 不在此处改变
        # print(self.lon, self.lat, self.speed, self.heading, distance, xx, yy)
        return x, y

    def SetSpeed(self, speed):
        self.speed = speed

    def SetHeading(self, heading):
        self.heading = heading

    def SetPosition(self, lon, lat):
        self.lon = lon
        self.lat = lat

    def GetAllShipStatusInSimVM(self):
        AllShipStatusInSimVM = []
        for ship in self.simVM.SimShhipRegistered:
            status = ship.GetSimShipStatus()
            AllShipStatusInSimVM.append({'status': status, 'id': ship.id})
        return AllShipStatusInSimVM

    # def MakeDecision(self, status=self.GetAllShipStatusInSimVM()):
    #     # 现在案例只有两船
    #     shipStatus = []
    #     for item in status:
    #         if item['id'] == self.id:
    #             pass
    #         else:
    #             shipStatus = item['status']
    #     GiveWay = HA.JudgeGiveWay([self.lon, self.lat], [shipStatus['lon'], shipStatus['lat']])
    #     if GiveWay:
    #         tc, delta_a1, v1new = HA.A1(self.heading, self.speed, [self.lon, self.lat], shipStatus['heading'], shipStatus['speed'], [shipStatus['lon'], shipStatus['lat']])
    #         if delta_a1 != 0:
    #             # 转向 然后前行
    #             self.Turn(delta_a1)
    #             self.SetSpeed(v1new)
    #             for i in range(int(tc/self.interval)):
    #                 x, y = self.Go()
    #                 self.SetPosition(x, y)
    #                 # TODO 借鉴v1 添加状态 append
    #                 # 下一步要添加进去
    #             pass
    #         else:
    #             # 通过减速即可避碰成功

    #             pass
    #     else:
    #         # 我是直航船
    #         x, y = self.GO()
    #         pass

class SimVM:
    def __init__(self, id, interval = 0.5, timeratio = 10, SysClock = 0):
        # 定义虚拟机内船舶清单
        # ShipStatus内存数据表，一台VM带一个
        # 初始化参数 其中的私有变量可以改为公有
        self.id = id # VMID
        self.interval = interval
        self.timeratio = timeratio
        self.SimShipRegistered = []
        self.__Times = 10
        self.__RunFlag = 0 # 测试决策
        self.__METFlag = 0 # 标识是否已经相遇，相遇则此虚拟机停止运行
        self.__SimData = []
        self.__NextStepData = {}
        self.DeciResult = {}
        self.SysClock = SysClock
        # 定义和启动VM线程

    def SetSysClock(self, clock):
        self.SysClock = clock

    def GetNextStepData(self):
        return self.__NextStepData

    def SetShipStatus(self, StatusData):
        """ 
        将ShipStatus 复原 
        """
        StatusData = copy.deepcopy(StatusData)
        i = 0
        for ship in self.SimShipRegistered:
            ship.__init__(
                StatusData[i].get('VMid'),
                StatusData[i].get('shipid'),
                StatusData[i].get('time'),
                StatusData[i].get('lon'),
                StatusData[i].get('lat'),
                StatusData[i].get('speed'),
                StatusData[i].get('heading'),
                StatusData[i].get('interval')
                )
            i += 1
        pass

    def GetMetFlag(self):
        return self.__METFlag

    def GetSimData(self):
        # time.sleep(0.1)
        return self.__SimData

    def addShip(self, ShipID, VM, Tick = 0, Lon = 0.0, Lat = 0.0, Speed = 0.0, Heading = 0.0):
        # 注册船舶
        ship = SimShip(self.id, ShipID, self, Tick, Lon, Lat, Speed, Heading, self.timeratio)
        self.SimShipRegistered.append(ship)
        # SimShipRegistered.append(ship)

    def delShip(self,):
        # 移除注册船舶 By shipid
        for ship in self.SimShipRegistered:
            if ship.VMid == self.id:
                self.SimShipRegistered.remove(ship)
            # if ship.id == shipid:
            #     self.SimShipRegistered.remove(ship)

    def pre_RunOneTime(self, ):
        for ship in self.SimShipRegistered:
            ship.RunOneDecision(self.__RunFlag)
        thisShipStatus = self.GetShipStatus()
        # print("请注意下面进入决策引擎的数据和数量，正常情况列表中应该只有2条数据: ")
        # print(thisShipStatus, '\n')
        DeciResult = HA.ProbDeciEngie(thisShipStatus)
        # print(DeciResult)
        self.__SimData.append(self.GetShipStatus())
        # print("FLAG: ", DeciResult["FLAG"], "\n")
        return DeciResult

    def RunOneTime(self):
        bar = []
        for ship in self.SimShipRegistered:
            flag = ship.RunOneStep()
            bar.append(flag)
            ship.update_tick()
        self.__SimData.append(self.GetShipStatus())
        if bar[0] + bar[1] > 0:
            return 1
        else:
            return 0

    def GetShipStatus(self):
        # time.sleep(0.1)
        foo = []
        for ship in self.SimShipRegistered:
        # for ship in SimShipRegistered:
            # print(ship.GetShipStatus())
            foo.append(ship.GetShipStatus())
        return foo
        pass


    def StoreVOImgDataAndAddID2ShipStatus(self):
        ShipStatus = self.GetShipStatus()
        pos1 = [ShipStatus[0]['lon'], ShipStatus[0]['lat']]
        heading1 = ShipStatus[0]['heading']
        speed1 = ShipStatus[0]['speed']

        pos2 = [ShipStatus[1]['lon'], ShipStatus[1]['lat']]
        heading2 = ShipStatus[1]['heading']
        speed2 = ShipStatus[1]['speed']
        # imgID 由 '11'和36位的uuid拼接而成
        imgID = '11' + str(uuid.uuid5(uuid.NAMESPACE_URL, str(time.time())))
        b64ImgData = DrawVoAreas.GenVOImgB64(pos1, heading1, speed1, pos2, heading2, speed2, imgID)
        # 将 b64压缩编码后的数据存入数据库，一次连接存储一条，有待优化
        # TODO:有待优化数据库操作
        opt_db.insert_into_voimg(imgID, self.id, b64ImgData)
        return imgID

    # 原始版本
    def pre_RunMultiTime(self):
        self.__GoHead = True
        # self.__RunFlag = True # 测试决策
        while self.__GoHead:
            if self.__Times == 0:
                self.__GoHead = False
            if self.__Times > 0:
                self.__Times = self.__Times - 1
            if self.__GoHead:
                # 调用上面的函数，存储图片数据，返回图片的ID
                imgID = self.StoreVOImgDataAndAddID2ShipStatus()
                # # 目前只有主船决策，两艘船的VOImg 图一样，向每一艘船中添加VOImgID
                # # 更好的方案应该是...不，不是...>这玩意儿就应该在虚拟机层面操作.
                # # 这玩意不应该在虚拟机层面操作
                thisDeciResult = self.RunOneTime() # 更新之后的
                for ship in self.SimShipRegistered:
                    ship.VOImgID = imgID # 向每一艘船中添加VOImgID
                    # ship.VOImgID = 10086 # 向每一艘船中添加VOImgID
                #     # 加入DCPA/TCPA的数据回传
                #     ship.DCPA = thisDeciResult['message']['DCPA']
                #     ship.TCPA = thisDeciResult['message']['TCPA']

                self.DeciResult = copy.deepcopy(thisDeciResult)
                self.__METFlag = thisDeciResult["MET"]
                if self.__METFlag == 1:
                    self.Stop()
                    # print("Attention:船已汇遇，当前虚拟机{}已经停止运行!\n".format(self.id))
                else:
                    self.__RunFlag = thisDeciResult["FLAG"]
                    # self.__RunFlag, DeciProb = self.RunOneTime() # 原来的
                    if thisDeciResult["FLAG"] == 1: 
                        self.Stop()
                        self.NextStep(thisDeciResult)

    # 新版本
    def RunMultiTime(self):
        self.__GoHead = True
        # self.__RunFlag = True # 测试决策
        while self.__GoHead:
            if self.__Times == 0:
                self.__GoHead = False
            if self.__Times > 0:
                self.__Times = self.__Times - 1
            if self.__GoHead:
                met_flag = self.RunOneTime() # 更新之后的
                imgID = self.StoreVOImgDataAndAddID2ShipStatus()
                for ship in self.SimShipRegistered:
                    ship.VOImgID = imgID # 向每一艘船中添加VOImgID
                    # ship.VOImgID = 10086 # 向每一艘船中添加VOImgID
                    # # 加入DCPA/TCPA的数据回传
                    # ship.DCPA = thisDeciResult['message']['DCPA']
                    # ship.TCPA = thisDeciResult['message']['TCPA']

                # self.DeciResult = copy.deepcopy(thisDeciResult)
                self.__METFlag = met_flag
                if self.__METFlag == 1:
                    self.Stop()
                    # print("Attention:船已汇遇，当前虚拟机{}已经停止运行!\n".format(self.id))
                else:
                    # self.__RunFlag = thisDeciResult["FLAG"]
                    # if thisDeciResult["FLAG"] == 1: 
                    #     self.Stop()
                    #     self.NextStep(thisDeciResult)
                    pass
    
    def NextStep(self, DeciProb):
        """
        系统决策：给出每个概率对应的下一步结果，经过组装之后以
        目前只有单船决策，即主船决策
        NextStepData = {
            "GoHead": {"prob": prob1, "status": ShipStatus1},
            "TurnLeft": {"prob": prob2, "status": ShipStatus2},
            "TurnRight": {"prob": prob3, "status": ShipStatus3}
        }
        的形式append到 self.__SimData 中,

        传入参数格式：
        DeciProb = {
            "FLAG": FLAG,
            "GoHead": GH,
            "TurnLeft": TL,
            "TurnRight": TR
        }
        其中GH, TL, TR均为概率数值,进入这里的FLAG 均为1，在这里已经没有用
        """
        DeciProb = copy.deepcopy(DeciProb)
        OldShipStatus = copy.deepcopy(self.GetShipStatus()) # ShipStatus
        # print('\nOldShipData: ', OldShipStatus)

        ShipStatus2 = self.RunNextStep(2)
        # TurnLeft = {"probability": DeciProb.get("TurnLeft"), "status": ShipStatus2}
        TurnLeft = {"probability": DeciProb.get("TurnLeft"), "status": OldShipStatus + ShipStatus2}
        # print('\nTurnLeft: ', TurnLeft)
        self.SetShipStatus(OldShipStatus)

        ShipStatus1 = self.RunNextStep(1)
        # GoHead = {"probability": DeciProb["GoHead"], "status": ShipStatus1}
        GoHead = {"probability": DeciProb["GoHead"], "status": OldShipStatus + ShipStatus1}
        # print('Prob: ', DeciProb["GoHead"])
        # print('\nGoHead: ', GoHead)
        self.SetShipStatus(OldShipStatus) # 将shipStatus 复原

        ShipStatus3 = self.RunNextStep(3)
        # TurnRight = {"probability": DeciProb.get("TurnRight"), "status": ShipStatus3}
        TurnRight = {"probability": DeciProb.get("TurnRight"), "status": OldShipStatus + ShipStatus3}
        # print('\nTurnRight: ', TurnRight)
        self.SetShipStatus(OldShipStatus)
        # print('\nAfterTurnRight ShipStatus: ', self.GetShipStatus())

        NextStepData = {
            "TurnLeft": TurnLeft,
            "GoHead": GoHead,
            "TurnRight": TurnRight
        }
        self.__NextStepData = copy.deepcopy(NextStepData)
        pass

    def RunNextStep(self, tempflag):
        """ 
        在功能上与RunOneTime相似，但又与之不同，单独作用一次，独立计算每种情况下的下一步的状态 
        """
        # ship1 = self.SimShipRegistered[0]
        # ship2 = self.SimShipRegistered[1]
        for ship in self.SimShipRegistered:
            ship.RunOneDecision(tempflag)

        SomeShipStatus = self.GetShipStatus()
        # print('\nThis SomeShipStatus: ', SomeShipStatus)
        return SomeShipStatus
        pass

    # def Run(self, initStatus4DrawLines, Times = 0):
    def Run(self, Times = 0):
        # 调用上面的函数，存储图片数据，返回图片的ID
        iimgID = self.StoreVOImgDataAndAddID2ShipStatus()
        # iimgID = 10086
        for ship in self.SimShipRegistered:
            ship.VOImgID = iimgID # 向每一艘船中添加VOImgID
        self.__SimData.append(self.GetShipStatus()) # 再将当前的起始状态添加到状态列表
        # 启动线程
        self.__Times = Times
        self.RunMultiTime()
        # self.__VMThread = threading.Thread(target=self.RunMultiTime(), args=(self,))
        # self.__VMThread.start()


    def Stop(self):
        self.__GoHead = False
        pass


# 这个函数用于外部调用
# def RunVM(initData, initStatus4DrawLines='random', interval = 0.2, timeRatio = 100, runTimes = -1):
#     """ 
#     : initData: data that init ships in this VM, and initData looks like :
#     initData = {
#         ship0: {
#             ShipID: "10086",
#             Tick: 0,
#             Lon: 123,
#             Lat: 35,
#             Speed: 10,
#             Heading: 90
#         },
#         ship1: {ShipID: "10010", Tick: 0, Lon: 123.1, Lat: 35.01, Speed: 7, Heading: 90}
#     }
#     : interval = 0.2,
#     : timeRatio = 100,
#     : runTimes = -1 : running times, -1 to loop,
#     : return: VMData
#     """
#     GenVMID = time.strftime("%y%m%d%H%M%S") + str(random.randint(1000, 9999))
#     # print("VMID: ", GenVMID)
#     VM = SimVM(id = GenVMID, interval = interval, timeratio = timeRatio)

#     if initStatus4DrawLines == 'random':
#         n_ships = 2
#         pos, course, speed = CreateEncounterSituation.Create(n_ships)
#         for i in range(n_ships):
#             VM.addShip(ShipID='STRI'+'-{}'.format(i), Lon=pos[i][0], Lat=pos[i][1], Speed=speed[i], Heading=course[i])
#     else: 
#         VM.addShip(
#             ShipID = initData["ship0"]["ShipID"], 
#             Tick = initData["ship0"]["Tick"],
#             Lon = initData["ship0"]["Lon"],
#             Lat = initData["ship0"]["Lat"],
#             Speed = initData["ship0"]["Speed"],
#             Heading = initData["ship0"]["Heading"]
#         ) # 主船
#         VM.addShip(ShipID = initData["ship1"]["ShipID"], Tick = initData["ship1"]["Tick"], Lon = initData["ship1"]["Lon"], Lat = initData["ship1"]["Lat"], Speed = initData["ship1"]["Speed"], Heading = initData["ship1"]["Heading"]) # 目标船，客船
    
#     # VM.addShip(
#     #     ShipID = initData["ship0"]["ShipID"], 
#     #     Tick = initData["ship0"]["Tick"],
#     #     Lon = initData["ship0"]["Lon"],
#     #     Lat = initData["ship0"]["Lat"],
#     #     Speed = initData["ship0"]["Speed"],
#     #     Heading = initData["ship0"]["Heading"]
#     # ) # 主船
#     # VM.addShip(ShipID = initData["ship1"]["ShipID"], Tick = initData["ship1"]["Tick"], Lon = initData["ship1"]["Lon"], Lat = initData["ship1"]["Lat"], Speed = initData["ship1"]["Speed"], Heading = initData["ship1"]["Heading"]) # 目标船，客船

#     VM.Run(initStatus4DrawLines, runTimes)
#     # VM.Run(runTimes)
#     # VMData = {"VMID": VM.id, "SimData": VM.GetSimData(), "NextStepData": VM.GetNextStepData(), "MET": VM.GetMetFlag()}
#     # print('\nVMData: ', VMData)
#     # return VMData
#     return VM


# 这个函数用于内部测试
def SimTest():
    GenVMID = time.strftime("%y%m%d%H%M%S") + str(random.randint(1000, 9999))
    # print("VMID: ", GenVMID)
    VM = SimVM(id = GenVMID, interval = 0.2, timeratio = 10)
    VM.addShip(ShipID='10086', VM=VM, Lon=122.995, Lat=34.995, Speed=9.8, Heading=10) # 主船
    VM.addShip(ShipID='10010', VM=VM, Lon=123.051, Lat=35.001, Speed=10.1, Heading=350) # 目标船，客船
    VM.Run(36)
    # VMData = {"VMID": VM.id, "SimData": VM.GetSimData(), "NextStepData": VM.GetNextStepData(), "MET": VM.GetMetFlag()}
    VMData = {"VMID": VM.id, "SimData": VM.GetSimData(), "NextStepData": VM.GetNextStepData(), "MET": VM.GetMetFlag(), 'DeciResult': VM.DeciResult}
    # VMData = {"VMID": VM.id, "SimData": VM.GetSimData(), "MET": VM.GetMetFlag()}
    # print('\nVMData: ', VMData)
    return VMData


# 这个函数用于内部测试随机生成初始条件情况下的仿真
def SimTestRandomInit():
    GenVMID = time.strftime("%y%m%d%H%M%S") + str(random.randint(1000, 9999))
    # print("VMID: ", GenVMID)
    VM = SimVM(id = GenVMID, interval = 0.2, timeratio = 100)
    n_ships = 2
    pos, course, speed = CreateEncounterSituation.Create(n_ships)
    # print(
    #     pos, type(pos), type(pos[0]), '\n', 
    #     course, type(course), '\n', 
    #     speed, type(speed), '\n'
    # )
    for i in range(n_ships):
        VM.addShip(ShipID='STRI'+'-{}'.format(i), Lon=pos[i][0], Lat=pos[i][1], Speed=speed[i], Heading=course[i])
    VM.Run(8)
    VMData = {"VMID": VM.id, "SimData": VM.GetSimData(), "NextStepData": VM.GetNextStepData(), "MET": VM.GetMetFlag()}
    # print('\nVMData: ', VMData)

from treelib import Tree
import json

def Tree_to_eChartsJSON(tree):
    #Transform the whole tree into an eCharts_JSON.
    def to_dict(tree, nid):
        ntag = tree[nid].tag
        tree_dict = {'name': ntag, 'value': int(nid), "children": []}
        #if tree[nid].expanded:
        for elem in tree.children(nid):
            tree_dict["children"].append(to_dict(tree, elem.identifier))
        if len(tree_dict["children"]) == 0:
            tree_dict.pop('children', None)
        return tree_dict
    eChartsDict = {'data': [to_dict(tree, tree.root)]}
    return json.dumps(eChartsDict)
    pass

def write2db(SimTreeID, sTree, VMpool):
    JSONTree = Tree_to_eChartsJSON(sTree)
    opt_db.insert_into_simtree(SimTreeID, JSONTree)
    for item in VMpool:
        opt_db.insert_into_simvm(item["VMID"], json.dumps(item))
    print("已经将仿真树和其中的结点数据写入数据库.")
    pass

def write2dynTree(sTree):
    opt_db.del_dynTree()
    allNodes = sTree.all_nodes()
    for node in allNodes:
        rootId = node.tag
        children = sTree.children(rootId)
        if (children is not None) and len(children) > 0:
            childrenArr = []
            for node in children:
                leafDic = {'name': node.tag, 'value': int(node.tag)}
                childrenArr.append(leafDic)
            childDic = {'data':[{'name': rootId, 'value': int(rootId), "children": childrenArr}]}
            # print(childDic)
            opt_db.insert_into_dynTree(rootId,json.dumps(childDic))
    pass

def main():
    Data = SimTest()
    tree = Tree()
    tree.create_node(identifier=Data["VMID"], parent=None)
    time.sleep(0.1)
    tree.create_node(identifier=time.strftime("%y%m%d%H%M%S") + str(random.randint(1000, 9999)), parent=Data["VMID"])
    time.sleep(0.1)
    tree.create_node(identifier=time.strftime("%y%m%d%H%M%S") + str(random.randint(1000, 9999)), parent=Data["VMID"])
    tree.show()
    write2dynTree(tree)
    write2db(Data["VMID"], tree, [Data])

    # SimTestRandomInit()
    pass

if __name__ == '__main__':
    main()
