# -*- coding:utf-8 -*-
import time
import base64
import hashlib
import requests
import json
import jsonpath

def sf_get_sign(dict_str):

    app_secret = "acdc9efb79db1fad06a59dea5f3eb5e3"
    list_dict = sorted(dict_str.keys())
    print(list_dict)
    str_list = app_secret
    for item in list_dict:
        if item == 'app_secret':
            continue
        str_list+=str(item)
        str_list += str(dict_str[item])

    str_list += app_secret

    print(str_list)
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
    sign=sf_get_sign(dict_str)
    print(sign)
    str_sign={"signature":sign}
    dict_str.update(str_sign)
    print(dict_str)

    payload = json.dumps(dict_str)

    print(payload)

    url="http://newopen.imdada.cn"+url_sz


    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
    return response.text

#do_dd

# url = "/api/order/addOrder"
url="/api/order/formalCancel"
# body= {
#     "shop_no": "63381-4279453",
#     "origin_id": "12312344342",
#     "city_code": "010",
#     "cargo_price": "12",
#     "is_prepay": "0",
#     "receiver_name": "张先生",
#     "receiver_phone": "13222221111",
#     "receiver_address": "三元桥",
#     "receiver_lat": "39.917683",
#     "receiver_lng": "116.467659",
#     "callback": "www.dosome.com",
#     "cargo_weight": "12",
#     "is_use_insurance": "0"
#     }
body= {

"order_id": "12312344342",
             "cancel_reason_id":"36",}
data_response=do_dada(url,body)

data_json = json.loads(data_response)

status = jsonpath.jsonpath(data_json, '$..status')[0]

print(status)