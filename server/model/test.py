
import TransBCD as BCD

# [0, -5.00] ，[3.83,3.21] ，[3.85, -2.22]，[-2.55, 2.55] 海里


# delta_meter -> delta lon, delta lat
# for item in [0, 3.83, 3.85, -2.55]:
#     print(123+BCD.DeltaMeter2DeltaLon(item*1852, 31))

# print()

# for item in [-5.00, 3.21, -2.22, 2.55]:
#     print(31+BCD.DeltaMeter2DeltaLat(item*1852))


# li = [1]
# if len(li) > 0:
#     print(li[0])
#     li = li[1:]
#     print(li)



# def remove_duplicated_decision(decision):
#     # decision = {
#     #     'deci_status': [{'id': ship.id, 'status': False}, {}, {}, {}],
#     #     'result': [{'id': ship.id, 'result': []}, {}, {}, {}]
#     #     'ship_status': [{}, {}, {}, {}]
#     # }
#     if len(decision['result']) > 4:
#         deci_status = decision['deci_status']  
#         result = decision['result']
#         foo_id = []
#         foo = []
#         deplicated_id = 0
#         for ds in deci_status:
#             id = ds['id']
#             # status = ds['status']
#             if id not in foo_id:
#                 foo_id.append(id)
#                 foo.append(ds)
#             else:
#                 deplicated_id = id
#                 for item in foo:
#                     if item['id'] == deplicated_id:
#                         item['status'] = True
#         bar = []  
#         d = []  
#         for res in result:
#             res_id = res['id']
#             res_result = res['result']
#             if res_id == deplicated_id:
#                 d.append(res)
#             else:
#                 bar.append(res)
#         d0 = d[0]
#         d1 = d[1]
#         if len(d[0]['result']) > len(d[1]['result']):
#             bar.append(d0)
#         else:
#             bar.append(d1)
#         decision['deci_status'] = foo
#         decision['result'] = bar
#     else:
#         pass
#     return decision

def new_remove_duplicated_decision(temp_deci_status, temp_result):
    # temp_deci_status = [{'id': ship.id, 'status': True}, {'id': ship.id, 'status': False}, {'id': ship.id, 'status': True},...]
    # temp_result = [{'id': ship.id, 'result': [0, 40, 50]}, {'id': ship.id, 'result': []}, {'id': ship.id, 'result': [10, 50, 40]}, ...]
    # 注：这些id一定是相同的 是当前船的id
    bar = False
    id = temp_deci_status[0]['id']
    for temp_d in temp_deci_status:
        if temp_d['status'] == True:
            bar = True
            break
    res = [[], [], []]
    for temp_r in temp_result:
        if len(temp_r['result']) > 0:
            res[0].append(temp_r['result'][0])
            res[1].append(temp_r['result'][1])
            res[2].append(temp_r['result'][2])
    if len(res[0]) > 0: #有东西
        max_res = [max(res[0]), max(res[1]), max(res[2])]
    else:
        max_res = []
    return {'id': id, 'status': bar}, {'id':id, 'result': max_res}



temp_deci_status = [{'id': 1, 'status': True}, {'id': 1, 'status': True}, {'id': 1, 'status': False}]
temp_result = [{'id': 1, 'result': [20, 40, 10]}, {'id': 1, 'result': []}, {'id': 1, 'result': [0, 30, 40]}]

# decision2 = {
#     'deci_status': [{'id': 1, 'status': False}, {'id': 2, 'status': False}, {'id': 3, 'status': False}, {'id': 4, 'status': False}, {'id': 4, 'status': True}],
#     'result': [{'id': 1, 'result': []}, {'id': 2, 'result': []}, {'id': 3, 'result': []}, {'id': 4, 'result': []}, {'id': 4, 'result': [0, 40, 50]}],
#     'ship_status': [{}, {}, {}, {}]
#     }
# decision3 = {
#     'deci_status': [{'id': 1, 'status': False}, {'id': 2, 'status': False}, {'id': 3, 'status': False}, {'id': 3, 'status': True}, {'id': 4, 'status': False}],
#     'result': [{'id': 1, 'result': []}, {'id': 2, 'result': []}, {'id': 3, 'result': []}, {'id': 3, 'result': [0, 30, 40]}, {'id': 4, 'result': []}],
#     'ship_status': [{}, {}, {}, {}]
#     }

d = new_remove_duplicated_decision(temp_deci_status, temp_result)
print(d)
