import json


# 去掉k和v里的全面空格
def remove_space(dict_tmp: dict):
    dict_res = {}
    for k, v in dict_tmp.items():
        if isinstance(k, str):
            k = k.replace(" ", "")
        if isinstance(v, str):
            v = v.replace(" ", "")

        dict_res[k] = v

    return dict_res


# 从多层嵌套里获取key的对应的值，ini里分割符是 = 或 : ，URL里把:替换成_
def check_key_dict_list_value(json_data, key):
    key = key.replace(':', '_')
    if isinstance(json_data, list):
        for i in json_data:
            if key in str(i): return check_key_dict_list_value(i, key=key)
    elif isinstance(json_data, dict):
        for k, v in json_data.items():
            if k == key:
                return v
            if key in str(v):
                return check_key_dict_list_value(v, key=key)
    else:
        try:
            return check_key_dict_list_value(json.loads(json_data), key=key)
        except:
            return


if __name__ == '__main__':
    lis = []
    json_data1 = {'key1': {'key2': [{'key3': 93, 'key4': 14}, {'key3': 93, 'key4': 15}]}, 'key5': 'test'}
    print(type(check_key_dict_list_value(json_data1, 'key6')))
    # print(lis)
