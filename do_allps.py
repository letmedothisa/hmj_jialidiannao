# -*- coding:utf-8 -*-
import hashlib
import time
import requests
import json
import jsonpath
import base64
import uuid

def do_ele(action_sz, params_sz):



    timestamp = int(time.time())
    uuid_ele = str(uuid.uuid4())

    app_key = "Z3Tqt3s69q"

    token = "326f16b37ccd95634625ede8cff7d2e9"
    secret = "a040fcb3eefbb6ca161c4c57780becda9c95a501"

    action = action_sz
    # 基本信息

    metas = {
        "app_key": app_key,
        "timestamp": timestamp
    }
    params = params_sz

    string_sign = str(action) + str(token)

    metas.update(params)

    list_data = list(metas.keys())

    sort_list = sorted(list_data)

    for item in sort_list:

        if isinstance(metas[item], dict):

            do = str(metas[item]).replace("'", '"').replace(' ', '')

            string_sign += item + '=' + str(do)

        elif isinstance(metas[item], int):

            string_sign += item + '=' + str(metas[item])

        else:

            string_sign += item + '=' + '"' + str(metas[item]) + '"'

    string_sign += secret

    string_sign.replace("'", '"').replace(' ', '')

    # 获取MD5字符串
    sig = hashlib.md5(string_sign.encode(encoding='utf-8')).hexdigest().upper()

    # 去获取订单信息

    elemedingdan = {
        "token": token,
        "nop": "1.0.0",
        "metas": {
            "app_key": app_key,
            "timestamp": str(timestamp)
        },
        "params": params,
        "action": action,
        "id": uuid_ele,
        "signature": sig
    }

    payload = json.dumps(elemedingdan)


    url = "https://open-api.shop.ele.me/api/v1"

    headers = {
        'Content-Type': 'application/json;charset=utf-8'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    time.sleep(0.5)

    data_json = response.json()

    return  data_json

def get_mtsign(data):
    sign_key = 'i0wl5fx35vfyekms'

    list_data = list(data.keys())
    string_sign = sign_key
    sort_list = sorted(list_data)

    for item in sort_list:
        if item == 'sign':
            continue
        string_sign += str(item)
        if item == 'biz':
            string_sign += str(data[item]).replace("'", '"')
        else:
            string_sign += str(data[item])

    sign = hashlib.sha1(string_sign.encode('utf-8')).hexdigest()

    return sign


def do_mt(url_sz, biz_sz):
    # 获取sign
    timestamp = int(time.time())
    biz = {'biz': biz_sz}
    basic_zd = {
        'appAuthToken': '5d579664aaa45e487c6dab03dbaaf595ed54468034c05ffe41a554781c8c2a479923dee7c442c471ab34b21e162a6956',
        'timestamp': timestamp, 'charset': 'utf-8', 'developerId': 100789, 'version': 2}
    basic_payload = basic_zd
    basic_zd.update(biz)

    sign = get_mtsign(basic_zd)

    # 获取配送费
    sign = {'sign': sign}
    fix_zd = json.dumps(biz_sz)
    biz = {'biz': fix_zd}

    basic_payload.update(biz)
    basic_payload.update(sign)

    url = url_sz

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data=basic_payload)

    time.sleep(0.5)

    data_json = json.loads(response.text)

    return  data_json

def do_sf(dict_str_sz, url_sz):

    dict_str = dict_str_sz
    jichu_url = url_sz

    push_str = (str(dict_str) + '&1547215874&98fd298d895379335a8d85a7ed5917c5').replace("'", '"')

    # 计算base64
    str_md5 = hashlib.md5(push_str.encode(encoding='utf-8')).hexdigest()
    bytes_url = str_md5.encode("utf-8")
    str_url = base64.b64encode(bytes_url)  # 被编码的参数必须是二进制数据
    str_url = str_url.decode('UTF-8')

    url = "https://openic.sf-express.com" + jichu_url + "sign=" + str(str_url)

    payload = json.dumps(dict_str, ensure_ascii=False)
    payload.replace(' ', '').replace("'", '"')
    payload.replace('\\', '')

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload.encode('utf-8'))

    time.sleep(0.5)

    data_json = response.json()

    return data_json

def dd_get_sign(dict_str):

    app_secret = "acdc9efb79db1fad06a59dea5f3eb5e3"
    list_dict = sorted(dict_str.keys())

    str_list = app_secret
    for item in list_dict:
        if item == 'app_secret':
            continue
        str_list+=str(item)
        str_list += str(dict_str[item])

    str_list += app_secret

    str_md5 = hashlib.md5(str_list.encode(encoding='utf-8')).hexdigest().upper()

    return str_md5

def do_dada(url_sz,body_sz):

    timestamp = int(time.time())

    dict_str = {
        "source_id": "63381",
        "v": "1.0",
        "format": "json",
        "app_key": "dadae480b0594b5b90c",
        }

    body_sz=str(body_sz).replace("'",'"').replace(' ','')
    dict_str.update({"body":body_sz})
    dict_str.update({"timestamp":str(timestamp)})
    sign=dd_get_sign(dict_str)

    str_sign={"signature":sign}
    dict_str.update(str_sign)


    payload = json.dumps(dict_str)


    url="http://newopen.imdada.cn"+url_sz


    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    time.sleep(0.5)

    data_json = json.loads(response.text)

    return data_json

#-------------------------------------------------测试分割线---------------------------------------------------------

