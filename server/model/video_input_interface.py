# 视频接口输入
import redis, json
import time, math, copy, random
import schedule


'''
Mock Human Status: 模拟视频输入接口,按照一定的时序返回人员状态

      _______                   ______------------                  ____________----------
______       __________---------                  --------__________                      ---------_______

标定4种状态,分别是: 0 正常, 1 离岗, 2 玩手机, 3 瞌睡
最小时间单位是: 5个时间单位
此中每个动作持续时间以: 5个时间单位 成比例翻倍, 例如分别持续5, 20, 15个时间单位等
将人员的行为预先标定出来, 记作 human_status, 人员状态是离散而有限的, 在时间维度上也不能无限标定
因此将循环利用 human_status, 可以使用取模的方式循环使用human_status.
由于human_status的时间基准是5个时间单位, 因此在获取人员状态时
只需将时间t除以5, 再用得到的结果作为索引值在human_status中查找
'''

human1_status = (1, 0, 0, 2, 0, 0, 1, 0, 3, 0, 0, 0, 0, 3, 0, 0, 1, 2, 0, 0)
human2_status = (1, 0, 3, 0, 0, 1, 2, 0, 0, 0, 0, 2, 0, 0, 1, 0, 3, 0, 0, 0)
human_status = (human1_status, human2_status)
# 每次从action_prob中随机选取一个值作为人员行为概率
action_prob = (0.82, 0.66, 0.67, 0.73, 0.79, 0.91, 0.68, 0.69, 0.85, 0.84, 0.76, 0.59, 0.98, 0.77, 0.87, 0.93, 0.84, 0.92, 0.79, 0.93)
# 用于计时(或者说计数)
T = 0

def get_human_status(human_status):
    global T
    assert T >= 0

    index = math.floor(T / 5) % len(human_status)
    return human_status[index]

def update_time():
    global T
    T = T + 1
    if T >= 2048:
        T = 0

''' 
# vii 样例
vii = {
    "timestamp": "47318742134",
    "human_num": 2,
    "humans": [
        {
            "human_id": 0,
            "action_id": 2,
            "action_prob": 0.69,
            "position": []
        },
        {
            "human_id": 1,
            "action_id": 1,
            "action_prob": 0.72,
            "position": []
        }        
    ]
}
'''

vii = {
    "timestamp": "1234567890123",
    "human_num": 0,
    "humans": [] 
}

def vii_builder():
    global human_status, action_prob
    vii_obj = copy.deepcopy(vii)
    vii_obj["timestamp"] = int(time.time() * 1000)

    human_num = 2 # suppose
    for i in range(human_num):
        vii_obj["humans"].append(
            {
            "human_id": i,
            "action_id": get_human_status(human_status[i]),
            "action_prob": random.sample(action_prob, 1)[0],
            "position": []
            } 
        )
    return vii_obj

def vii_sender(redis_link, vii_obj):
    print("vii_obj:",vii_obj)
    # redis_link.set("vii_obj", json.dumps(vii_obj))

def link_redis():
    return redis.StrictRedis(host='localhost', port=6379, db=0)

def job(redis_link):
    global T
    vii_obj = vii_builder()
    vii_sender(redis_link, vii_obj)
    update_time()

if __name__ == "__main__":
    # 连接redis
    R = link_redis()
    schedule.every(3).seconds.do(job, R)
    while True:
        schedule.run_pending()