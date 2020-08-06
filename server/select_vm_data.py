import json
import opt_db


def get_value(a_list, vmid_list):
    for item in a_list:
        value = item["value"] 
        vmid_list.append(value)
        if "children" in item:
            get_value(item["children"], vmid_list)

def write2file(tree_id):
    tree = opt_db.select_from_simtree(tree_id)[1]
    # print(tree)
    tree = json.loads(tree)
    vmid_list = []
    tree_data = tree["data"]
    get_value(tree_data, vmid_list)

    vm_list = []
    # 这里已经更新了vmid_list
    # print(vmid_list)
    tree = {"treeid": tree_id, "node": []}
    for vmid in vmid_list:
        vm_data = opt_db.select_from_simvm(str(vmid))
        vm_list.append(vm_data[1])

    for vm in vm_list:
        vm = json.loads(vm)
        with open('./server/data/{}.json'.format(str(vm['VMID'])), 'w+', encoding='utf-8') as f:
            sim_data = vm['SimData']
            f.write('{"data": [\n')
            for item in sim_data:
                for ship in item:
                    if (item.index(ship) == (len(item) -1)) and (sim_data.index(item) == len(sim_data) -1):
                        # 最后一个 后面不能加逗号
                        f.write(json.dumps(ship))
                        f.write('\n')
                    else:
                        f.write(json.dumps(ship))
                        f.write(',\n')
            f.write(']}\n')
            f.close()
def main():
    tree_id = '102008061608223461'
    write2file(tree_id)
    print('当前仿真树:{}中结点数据以写入/server/data/下，每个结点的数据对应一个文件.'.format(str(tree_id)))


if __name__ == "__main__":
    main()
