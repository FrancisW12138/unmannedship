import math
import copy
import TransBCD
import CPA

class SimShip:
    def __init__(self, SimVMID, ShipID, SVM, Tick = 0, Lon = 0.0, Lat = 0.0, Speed = 0.0, Heading = 0.0, TimeRatio = 10, ):
        self.VMid     = SimVMID   # 所属虚拟机
        self.id       = ShipID    #船舶的ID号码
        self.lon      = Lon       #船舶经度坐标
        self.lat      = Lat       #船舶纬度坐标
        self.speed    = Speed     #船舶速度,m/s
        self.heading  = Heading   #船艏向，°，正北方向为 0，顺时针旋转为正
        self.interval = TimeRatio #一次离散步长所对应的时间间隔
        self.tick     = Tick      #当前虚拟时钟
        # self.VOImgID = None
        self.DCPA  =  9999
        self.TCPA = 9999
        self.simVM = SVM
        self.original_speed = Speed
        self.original_heading = Heading
        self.radar_range = 1852 # TODO 注意 米和经纬度
        self.decision_status = False
        self.decision_content = [] # 决策内容
        self.instructions_queue = [] # 指令队列
        self.full_decision_length = 0
        self.applied_decision_lenth = 0
        # self.mtc = 0
        # self.instructions_status

    def turn_left(self):
        self.heading -= 5
    
    def turn_right(self):
        self.heading += 5
    
    def go_ahead(self):
        distance = self.speed * self.interval # 单位为米
        x_com = distance * math.sin(math.radians(self.heading))
        y_com = distance * math.cos(math.radians(self.heading))
        xx = TransBCD.DeltaMeter2DeltaLon(x_com, self.lat)
        yy = TransBCD.DeltaMeter2DeltaLat(y_com)
        self.lon += xx
        self.lat += yy
        print('已前进，当前位置', self.lon, self.lat)

    def instructions_mapping(self, instruction_code):
        if instruction_code == 1001:
            self.turn_left()
        elif instruction_code == 1002:
            self.turn_right()
        else:
            self.go_ahead()

    def set_original_status(self):
        self.speed = self.original_speed
        self.heading = self.original_heading

    def execute_instruction(self):
        ins = self.instructions_queue
        if len(ins) > 0:
            # 当前还处在执行决策阶段 指令还没执行完毕
            this_ins = ins[0]
            for step in this_ins:
                self.instructions_mapping(step)
            self.instructions_queue = ins[1:] #更新
            self.applied_decision_lenth += 1
            if self.applied_decision_lenth == self.full_decision_length:
                self.set_original_status()
        else:
            self.go_ahead()

    def detect_ship_in_radar_range(self):
        ship_in_range = []
        for ship in self.simVM.SimShhipRegistered:
            if ship.id == self.id:
                pass
            else:
                dis = math.hypot(self.lon - ship.lon, self.lat - ship.lat)
                if dis < self.radar_range:
                    ship_in_range.append(ship)
                else:
                    pass
        return ship_in_range

    def get_decision_probability(self, DCPA):
        return math.exp(self.DCPA * 1.05 * (-1) / 1000)

    def get_ship_status(self):
        shipStatus = {} # 创建一个空字典
        shipStatus['time'] = self.tick
        shipStatus['VMid'] = self.VMid
        shipStatus['shipid'] = self.id
        shipStatus['lon'] = self.lon
        shipStatus['lat'] = self.lat
        shipStatus['speed'] = self.speed
        shipStatus['heading'] = self.heading
        shipStatus['interval'] = self.interval
        # shipStatus['VOImgID'] = self.VOImgID
        shipStatus['DCPA'] = self.DCPA
        shipStatus['TCPA']  = self.TCPA
        shipStatus['simVM'] = self.simVM
        shipStatus['original_speed'] = self.original_speed
        shipStatus['original_heading'] = self.original_heading
        shipStatus['radar_range'] = self.radar_range
        shipStatus['decision_status'] = self.decision_status
        shipStatus['decision_content'] = self.decision_content
        shipStatus['instructions_queue'] = self.instructions_queue
        shipStatus['full_decision_length'] = self.full_decision_length
        shipStatus['applied_decision_lenth'] = self.applied_decision_lenth
        return shipStatus


class SimVM:
    def __init__(self, id, interval = 0.5, timeratio = 10):
        # 定义虚拟机内船舶清单
        # ShipStatus内存数据表，一台VM带一个
        # 初始化参数 其中的私有变量可以改为公有
        self.id = id # VMID
        self.interval = interval
        self.timeratio = timeratio
        self.SimShipRegistered = []
        self.Times = 10
        self.RunFlag = 0 # 测试决策
        self.METFlag = 0 # 标识是否已经相遇，相遇则此虚拟机停止运行
        self.SimData = []
        self.NextStepData = {}
        self.DeciResult = {}
        # self.SysClock = SysClock

    def addShip(self, ShipID, VM, Tick = 0, Lon = 0.0, Lat = 0.0, Speed = 0.0, Heading = 0.0):
        ship = SimShip(self.id, ShipID, self, Tick, Lon, Lat, Speed, Heading, self.timeratio)
        self.SimShipRegistered.append(ship)

    def delShip(self,):
        for ship in self.SimShipRegistered:
            if ship.VMid == self.id:
                self.SimShipRegistered.remove(ship)

    def get_all_ship_status(self):
        foo = []
        for ship in self.SimShipRegistered:
            foo.append(ship.GetShipStatus())
        return foo

    def stop(self):
        self.GoHead = False
        pass

    def parse_decition(self, a_ship_decision):
        # decision looks like: [GW1_vc_max, GW2_ac_max, GW2_tc_max]
        # 注意 只有让路船会决策 故不存在左转的情况
        # 注意 只解析GW2_tc_max 不解析速度和角度的改变 
        # 因为假设速度和角度的改变不消耗时间 应在调用此函数之前或之后一次操作完成
        dt = 10
        ins = []
        GW2_tc_max =  a_ship_decision[2]
        for t in range(int(GW2_tc_max/dt)):
            ins.append(2001)
        return ins

    def pre_gen_branch_data(self, decision):
        # decision = {
        #     'deci_status': [{'id': ship.id, 'status': False}, {}, {}, {}],
        #     'result': [{'id': ship.id, 'result': []}, {}, {}, {}]
        #     'ship_status': [{}, {}, {}, {}]
        # }
        data1 = self.get_all_ship_status() # 保持状态的分支数据
        data2 = [] # 新分支的数据
        data1 = copy.deepcopy(self)
        data2 = copy.deepcopy(self)


        for ship in self.SimShipRegistered:
            temp_ins = []
            bar = copy.deepcopy(ship)
            break_flag = False
            for ds in decision['deci_status']:
                if ds['id'] == bar.id and ds['status'] == True: # 找到‘我’,且我做了新决策
                    # 去找‘我’的决策内容
                    for res in decision['result']:
                        if res['id'] == bar.id:
                            # 读决策结果 解析为指令
                            temp_ins = self.parse_decition(res['result']) 
                            bar.instructions_queue = temp_ins 

                            # 在此改变速度和方向 上面的解析指令中不解析速度和方向
                            bar.speed = bar.speed - res['result'][0] 
                            bar.heading = bar.heading - res['result'][1]
                            
                            break_flag = True
                            data2.append(bar.get_ship_status())
                            break
                if break_flag:
                    break
        # 继续 此处data2已经重新填好数据
        return data1, data2

    def gen_branch_data(self, decision):
        # decision = {
        #     'deci_status': [{'id': ship.id, 'status': False}, {}, {}, {}],
        #     'result': [{'id': ship.id, 'result': []}, {}, {}, {}]
        #     'ship_status': [{}, {}, {}, {}]
        # }
        VM1 = copy.deepcopy(self)
        VM2 = copy.deepcopy(self)
        for ship in VM2.SimShipRegistered:
            temp_ins = []
            break_flag = False
            for ds in decision['deci_status']:
                if ds['id'] == ship.id and ds['status'] == True: # 找到‘我’,且我做了新决策
                    # 去找‘我’的决策内容
                    for res in decision['result']:
                        if res['id'] == ship.id:
                            # 读决策结果 解析为指令
                            temp_ins = self.parse_decition(res['result']) 
                            ship.instructions_queue = temp_ins
                            ship.full_decision_length = len(temp_ins)

                            # 在此改变速度和方向 上面的解析指令中不解析速度和方向
                            ship.speed = ship.speed - res['result'][0] 
                            ship.heading = ship.heading - res['result'][1]

                            break_flag = True
                            break
                if break_flag:
                    break
        return VM1, VM2

    def Run(self, Times = 32):
        will_brance = False
        decision = {
            'deci_status': [],
            'result': [],
            'ship_status': []
        }
        self.GoHead = True
        self.SimData.append(self.GetShipStatus()) # 再将当前的起始状态添加到状态列表
        self.Times = Times
        while self.GoHead:
            if self.Times == 0:
                self.GoHead = False
            if self.Times > 0:
                self.Times = self.Times - 1
            if self.GoHead:
                will_brance, decision = self.RunOneTime() # 更新之后的
                if will_brance:
                    # 要分支 则本虚拟机停止
                    self.stop()
                else:
                    pass
        # 结束之后
        if will_brance:
            VM1, VM2 = self.gen_branch_data(decision)
            # TODO 下一步
            pass
        else:
            # TODO 下一步
            pass

    def RunOneTime(self, ):
        # 注：decision是本轮决策结果
        decision = {
            'deci_status': [],
            'result': [],
            'ship_status': []
        }
        original_decision_status = []
        for ship in self.SimShipRegistered:
            original_decision_status.append(ship.decision_status)
            if ship.decision_status:
                # 如果ship已经做出决策
                if ship.applied_decision_lenth < ship.full_decision_length:
                    ship.execute_instruction()
                else:
                    ship.set_original_status()
                    ship.go_ahead()
                decision['deci_status'].append({'id': ship.id, 'status': False})
                decision['result'].append({'id': ship.id, 'result': []})
                decision['ship_status'].append({'id': ship.id, 'ship_status': ship.get_ship_status()})
            else:
                # ship尚未做出决策
                ship_in_range = ship.detect_ship_in_radar_range()
                if len(ship_in_range) > 0:
                    for target_ship in ship_in_range:
                        JDCPA = CPA.JDCPA(target_ship) # 算法1
                        p = ship.get_decision_probability(JDCPA)
                        if p > 0.8:
                            deci_result = ship.AHLD() # 算法2
                            ship.decision_status = True
                            ship.decision_content = [deci_result]
                            # deci_result looks like: GW1_vc_max, GW2_ac_max, GW2_tc_max
                            decision['deci_status'].append({'id': ship.id, 'status': True})
                            decision['result'].append({'id': ship.id, 'result': [deci_result]})
                            decision['ship_status'].append({'id': ship.id, 'ship_status': ship.get_ship_status()})
                        else:
                            decision['deci_status'].append({'id': ship.id, 'status': False})
                            decision['result'].append({'id': ship.id, 'result': []})
                            decision['ship_status'].append({'id': ship.id, 'ship_status': ship.get_ship_status()})
                else:
                    # 领域内没有船
                    decision['deci_status'].append({'id': ship.id, 'status': False})
                    decision['result'].append({'id': ship.id, 'result': []})
                    decision['ship_status'].append({'id': ship.id, 'ship_status': ship.get_ship_status()})
        for elem in decision['deci_status']:
            if elem['status'] == True:
                will_branch = True
                break
        else:
            will_branch = False
        self.SimData.append(self.get_all_ship_status())
        return will_branch, decision


def test():
    VM = SimVM(id, interval=0.5, timeratio=10)
    VM.addShip(ShipID='1', VM=VM, Tick=0, Lon=123, Lat=31, Speed=10, Heading=10)
    VM.addShip(ShipID='2', VM=VM, Tick=0, Lon=123, Lat=31, Speed=10, Heading=10)
    VM.addShip(ShipID='3', VM=VM, Tick=0, Lon=123, Lat=31, Speed=10, Heading=10)
    VM.addShip(ShipID='4', VM=VM, Tick=0, Lon=123, Lat=31, Speed=10, Heading=10)
    VM.Run()
    pass