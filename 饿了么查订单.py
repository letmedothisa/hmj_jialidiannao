# -*- coding:utf-8 -*-
import json
import time
import uuid
import hashlib
import requests
import jsonpath


def do_ele(order_id, action_sz, params_sz):
  timestamp = int(time.time())
  order_id = str(order_id)
  uuid_ele = str(uuid.uuid4())
  app_key = "Z3Tqt3s69q"
  token = "ac2aae02ce781994ddad70eab7588a4c"
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
  print(string_sign)

  # 获取MD5字符串
  sig = hashlib.md5(string_sign.encode(encoding='utf-8')).hexdigest().upper()

  print(sig)
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

  print(elemedingdan)

  url = "https://open-api.shop.ele.me/api/v1"

  headers = {
    'Content-Type': 'application/json;charset=utf-8'
  }

  response = requests.request("POST", url, headers=headers, data=payload)

  print(response.text)

  # data_json = response.json()
  #
  # error_code = jsonpath.jsonpath(data_json, '$..error_code')[0]
  #
  # return error_code


# 饿了么同步配送信息
orderid = "8533349187965074821"

action = "eleme.order.delivery.getDeliveryRoutes"

params = {

    "orderId": orderid,

}

do_ele(orderid, action, params)