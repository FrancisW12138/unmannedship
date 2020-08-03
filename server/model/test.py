
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



def remove_duplicated_decision(decision):
    # decision = {
    #     'deci_status': [{'id': ship.id, 'status': False}, {}, {}, {}],
    #     'result': [{'id': ship.id, 'result': []}, {}, {}, {}]
    #     'ship_status': [{}, {}, {}, {}]
    # }
    if len(decision['result']) > 4:
        deci_status = decision['deci_status']  
        result = decision['result']
        foo_id = []
        foo = []
        deplicated_id = 0
        for ds in deci_status:
            id = ds['id']
            # status = ds['status']
            if id not in foo_id:
                foo_id.append(id)
                foo.append(ds)
            else:
                deplicated_id = id
                for item in foo:
                    if item['id'] == deplicated_id:
                        item['status'] = True
        bar = []  
        d = []  
        for res in result:
            res_id = res['id']
            res_result = res['result']
            if res_id == deplicated_id:
                d.append(res)
            else:
                bar.append(res)
        d0 = d[0]
        d1 = d[1]
        if len(d[0]['result']) > len(d[1]['result']):
            bar.append(d0)
        else:
            bar.append(d1)
        decision['deci_status'] = foo
        decision['result'] = bar
    else:
        pass
    return decision




decision = {
    'deci_status': [{'id': 1, 'status': False}, {'id': 2, 'status': False}, {'id': 3, 'status': False}, {'id': 4, 'status': False}],
    'result': [{'id': 1, 'result': []}, {'id': 2, 'result': []}, {'id': 3, 'result': []}, {'id': 4, 'result': []}],
    'ship_status': [{}, {}, {}, {}]
    }
decision2 = {
    'deci_status': [{'id': 1, 'status': False}, {'id': 2, 'status': False}, {'id': 3, 'status': False}, {'id': 4, 'status': False}, {'id': 4, 'status': True}],
    'result': [{'id': 1, 'result': []}, {'id': 2, 'result': []}, {'id': 3, 'result': []}, {'id': 4, 'result': []}, {'id': 4, 'result': [0, 40, 50]}],
    'ship_status': [{}, {}, {}, {}]
    }
decision3 = {
    'deci_status': [{'id': 1, 'status': False}, {'id': 2, 'status': False}, {'id': 3, 'status': False}, {'id': 3, 'status': True}, {'id': 4, 'status': False}],
    'result': [{'id': 1, 'result': []}, {'id': 2, 'result': []}, {'id': 3, 'result': []}, {'id': 3, 'result': [0, 30, 40]}, {'id': 4, 'result': []}],
    'ship_status': [{}, {}, {}, {}]
    }

d = remove_duplicated_decision(decision3)
print(d)
