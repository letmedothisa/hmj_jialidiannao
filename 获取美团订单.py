# -*- coding:utf-8 -*-
import datetime
import mysql_tengxun
from escpos.printer import Network
import hashlib
import time
import requests
import json
import jsonpath
import os
from PIL import Image, ImageFont, ImageDraw
import sys
from tkinter import messagebox
import uuid

""" Seiko Epson Corp. Receipt Printer M129 Definitions (EPSON TM-T88IV) """


def print_order(ipconfig,pic_name_title, pic_name_content, pic_name_tail):

    if ipconfig==188:
        p = Network("192.168.1.188")
    elif ipconfig==189:
        p = Network("192.168.1.189")
    elif ipconfig==190:
        p = Network("192.168.1.190")
    elif ipconfig==191:
        p = Network("192.168.1.191")
    elif ipconfig==192:
        p = Network("192.168.1.192")

    p.codepage = 'GB18030'
    # 打印订单信息
    p.image(pic_name_title)
    p.text('-')
    p.text('\n')
    p.image(pic_name_content)
    p.text('-')
    p.text('\n')
    p.image(pic_name_tail)
    p.cut()


def get_sign(data):
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
    print(string_sign)
    sign = hashlib.sha1(string_sign.encode('utf-8')).hexdigest()
    return sign


def get_elemedingdan(order_id):

    timestamp = int(time.time())
    orderid = str(order_id)
    uuid_ele = str(uuid.uuid4())
    app_key = "Z3Tqt3s69q"
    token = "14d1a44d18b4badf0e09e1fa86e1875b"
    secret = "a040fcb3eefbb6ca161c4c57780becda9c95a501"
    action = "eleme.order.getOrder"

    # 基本信息

    metas = {
        "app_key": app_key,
        "timestamp": str(timestamp)
    }
    params = {
        "orderId": orderid
    }

    string_sign = str(action) + str(token)

    metas.update(params)

    list_data = list(metas.keys())

    sort_list = sorted(list_data)

    for item in sort_list:
        if item != 'timestamp':
            string_sign += item + '=' + '"' + metas[item] + '"'

        else:
            string_sign += item + '=' + metas[item]

    string_sign += secret

    print(string_sign)

    # 定义MD5
    hmd5 = hashlib.md5()
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
        "params": {
            "orderId": orderid
        },
        "action": action,
        "id": uuid_ele,
        "signature": sig
    }

    print(elemedingdan)

    payload = json.dumps(elemedingdan)

    url = "https://open-api.shop.ele.me/api/v1/"

    headers = {
        'Content-Type': 'application/json;charset=utf-8'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.text

def get_dingdan(orderid):
    # 获取sign
    timestamp = int(time.time())
    order_id = str(orderid)
    biz = {'biz': {"orderId": order_id}}
    basic_zd = {
        'appAuthToken': '5d579664aaa45e487c6dab03dbaaf595ed54468034c05ffe41a554781c8c2a479923dee7c442c471ab34b21e162a6956',
        'timestamp': timestamp, 'charset': 'utf-8', 'developerId': 100789, 'version': 2}
    basic_payload = basic_zd
    basic_payload_2 = basic_zd
    basic_zd.update(biz)

    sign = get_sign(basic_zd)

    # 获取配送费
    sign = {'sign': sign}
    fix_zd = json.dumps({"orderId": order_id})
    biz = {'biz': fix_zd}

    basic_payload.update(biz)
    basic_payload.update(sign)

    url = "https://api-open-cater.meituan.com/waimai/order/queryById"

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data=basic_payload)

    return response.text




shangpin = get_dingdan('18488792624001381')

print(shangpin)