# -*- coding:utf-8 -*-
import datetime
import mysql_tengxun
import hashlib
import time
import requests
import json
import base64
import jsonpath
import threading
import uuid


def get_sfstatus(orderid):
    timestamp = int(time.time())
    jichu_url = "/open/api/external/getorderstatus?"

    dict_str = {
        "order_id": str(orderid),
        "order_type": "1",
        "dev_id": "1547215874",
        "push_time": str(timestamp)
    }

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
    print(payload)
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload.encode('utf-8'))

    data_json = response.json()

    error_code = jsonpath.jsonpath(data_json, '$..error_code')[0]
    status_code = jsonpath.jsonpath(data_json, '$..order_status')[0]
    rider_name = jsonpath.jsonpath(data_json, '$..rider_name')[0]
    rider_phone = jsonpath.jsonpath(data_json, '$..rider_phone')[0]

    return error_code, status_code, rider_name, rider_phone


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


def creat_ele(order_id):

    timestamp = int(time.time())
    orderid = str(order_id)
    uuid_ele = str(uuid.uuid4())
    app_key = "Z3Tqt3s69q"
    token = "ac2aae02ce781994ddad70eab7588a4c"
    secret = "a040fcb3eefbb6ca161c4c57780becda9c95a501"
    action = "eleme.order.callDelivery"

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

    # 定义MD5
    hmd5 = hashlib.md5()
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
        "params": {
            "orderId": orderid
        },
        "action": action,
        "id": uuid_ele,
        "signature": sig
    }

    payload = json.dumps(elemedingdan)

    url = "https://open-api.shop.ele.me/api/v1/"

    headers = {
        'Content-Type': 'application/json;charset=utf-8'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    data_json = response.json()

    error_code = jsonpath.jsonpath(data_json, '$..error')

    return error_code


def creat_sf(orderid, order_source, order_num, order_time, costomer, costomer_phone, costomer_address, costomer_lng,
             costomer_lat, total_price):
    timestamp = int(time.time())

    jichu_url = "/open/api/external/createorder?"

    # 转换为时间戳
    order_time = str(order_time)
    order_time = time.strptime(order_time, "%Y-%m-%d %H:%M:%S")
    order_time = int(time.mktime(order_time))
    # total_price 转为分
    total_price = int(total_price * 100)
    # 经纬度转换一下
    costomer_lng = str(costomer_lng / 1000000)
    costomer_lat = str(costomer_lat / 1000000)

    dict_str = {
        "shop_id": "6250508608337",
        "shop_order_id": str(orderid),
        "dev_id": "1547215874",
        "order_source": str(order_source),
        "order_sequence": str(order_num),
        "pay_type": "1",
        "lbs_type": "2",
        "order_time": str(order_time),
        "is_appoint": "0",
        "is_person_direct": "0",
        "push_time": str(timestamp),
        "version": "17",
        "is_insured": "0",
        "receive": {
            "user_name": str(costomer),
            "user_phone": str(costomer_phone),
            "user_address": str(costomer_address),
            "user_lng": str(costomer_lng),
            "user_lat": str(costomer_lat)
        },
        "order_detail": {
            "total_price": str(total_price),
            "product_type": "1",
            "weight_gram": "1000",
            "product_num": "1",
            "product_type_num": "1",
            "product_detail": ["hmj", "2"]
        }
    }

    push_str = (str(dict_str) + '&1547215874&98fd298d895379335a8d85a7ed5917c5').replace("'", '"')

    print(push_str)
    # 计算base64
    str_md5 = hashlib.md5(push_str.encode(encoding='utf-8')).hexdigest()
    bytes_url = str_md5.encode("utf-8")
    str_url = base64.b64encode(bytes_url)  # 被编码的参数必须是二进制数据
    str_url = str_url.decode('UTF-8')

    url = "https://openic.sf-express.com" + jichu_url + "sign=" + str(str_url)

    payload = json.dumps(dict_str, ensure_ascii=False)
    payload.replace(' ', '').replace("'", '"')
    payload.replace('\\', '')
    print(payload)
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload.encode('utf-8'))

    data_json = response.json()

    error_code = jsonpath.jsonpath(data_json, '$..error_code')[0]
    sf_order_id = jsonpath.jsonpath(data_json, '$..sf_order_id')[0]

    return error_code, sf_order_id


def cancel_sf(orderid):
    timestamp = int(time.time())

    dict_str = {
        "order_id": str(orderid),
        "order_type": "1",
        "dev_id": "1547215874",
        "push_time": str(timestamp)
    }
    push_str = (str(dict_str) + '&1547215874&98fd298d895379335a8d85a7ed5917c5').replace("'", '"')

    # 计算base64
    str_md5 = hashlib.md5(push_str.encode(encoding='utf-8')).hexdigest()
    bytes_url = str_md5.encode("utf-8")
    str_url = base64.b64encode(bytes_url)  # 被编码的参数必须是二进制数据
    str_url = str_url.decode('UTF-8')

    url = "https://openic.sf-express.com/open/api/external/cancelorder?sign=" + str(str_url)

    payload = json.dumps(dict_str)
    payload.replace("'", '"')

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    data_json = response.json()

    error_code = jsonpath.jsonpath(data_json, '$..error_code')[0]

    return error_code


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

    payload = json.dumps(dict_str)
    payload.replace("'", '"')

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    data_json = response.json()

    return data_json


def get_eleorder():
    data_sql = []

    now_time = datetime.datetime.now() + datetime.timedelta(hours=-3)

    sql = "SELECT * FROM order_2 WHERE order_2.platform = '%s' and order_2.creat_time > '%s'  and order_2.dingdan_status!='%s' and order_2.peisongy='%s' and order_2.ps_record is NULL" % (
        '饿了么', now_time, -4, 'None')

    while 1:
        try:
            data_sql = mysql_tengxun.mysql_getdata(sql)
            break

        except:
            time.sleep(1)
            print('get jiroudone data error')

    return data_sql


def cancel_order():


    print('取消订单检查')

    now_time = datetime.datetime.now() + datetime.timedelta(hours=-1)

    sql = "SELECT * FROM ps_record WHERE ps_record.ele_fadantime is NULL  and ps_record.platform='%s' and ps_record.sf_taketime is NULL and ps_record.creat_time > '%s'" % ('饿了么',
        now_time)

    while 1:
        try:
            data_sql = mysql_tengxun.mysql_getdata(sql)
            break

        except:
            time.sleep(1)
            print('get ps_record data error')

    if data_sql:
        for data in data_sql:

            if data[4] == None and data[6] == None:

                if (datetime.datetime.now() - data[3]).seconds > 600:

                    error_code = cancel_sf(data[5])

                    if error_code == 0:
                        sql = "update ps_record set cancel_time = '%s' where orderid='%s' " % (
                            datetime.datetime.now(), data[2])

                        while 1:
                            try:
                                mysql_tengxun.mysql_db(sql)
                                break
                            except:
                                time.sleep(1)
                                print('update_ps_record_error')
                                continue

                    if data[7] == None:

                        error_code = creat_ele(data[2])
                        print(error_code)

                        if error_code[0] == None:

                            sql = "update ps_record set ele_fadantime = '%s' where orderid='%s' " % (
                                datetime.datetime.now(), data[2])

                            while 1:
                                try:
                                    mysql_tengxun.mysql_db(sql)
                                    break
                                except:
                                    time.sleep(1)
                                    print('update_ele_fadantime_error')
                                    continue

                else:
                    error_code, status_code, rider_name, rider_phone = get_sfstatus(data[5])

                    if error_code == 0:
                        if status_code != 1 and status_code != 2:

                            sql = "update order_2 set peisongy = '%s',peisongy_phone= '%s' where order_id='%s' " % (
                                rider_name, rider_phone, data[2])

                            while 1:
                                try:
                                    mysql_tengxun.mysql_db(sql)
                                    break
                                except:
                                    time.sleep(1)
                                    print('update_order2_error')
                                    continue

                            sql = "update ps_record set sf_taketime = '%s',sf_status='%s' where orderid='%s' " % (
                                datetime.datetime.now(), 10, data[2])

                            while 1:
                                try:
                                    mysql_tengxun.mysql_db(sql)
                                    break
                                except:
                                    time.sleep(1)
                                    print('update_sf_taketime_error')
                                    continue

                            # 饿了么同步配送信息
                            orderid = data[2]

                            action = "eleme.order.selfDeliveryStateSync"

                            params = {
                                "shopId": 155852887,
                                "stateInfo": {
                                    "orderId": orderid,
                                    "distributorId": 201,
                                    "knight": {
                                        "id": "",
                                        "phone": "",
                                        "name": ""
                                    },
                                    "state": "DELIVERY_START",
                                    "deliveryCompanyId": 1000274550,
                                    "deliveryCompanyName": "配送公司名称"
                                }
                            }

                            do_ele(orderid, action, params)

    # 声明全局变量
    global t2
    # 创建并初始化线程
    t2 = threading.Timer(3, cancel_order)
    # 启动线程
    t2.start()


def creat_order():
    print('进来发单了')
    order_data = get_eleorder()

    print(order_data)

    if order_data:
        for data in order_data:
            orderid = data[9]
            order_source = '2'
            order_num = data[6]
            order_time = data[1]
            costomer = data[19]
            costomer_phone = data[3].replace('[', '').replace(']', '').replace('"', '')
            costomer_address = data[2]
            costomer_lng = data[14]
            costomer_lat = data[13]
            total_price = data[8]
            platform = data[4]

            error_code, sf_id = creat_sf(orderid, order_source, order_num, order_time, costomer, costomer_phone,
                                         costomer_address, costomer_lng, costomer_lat, total_price)

            print(error_code, sf_id)

            if error_code == 0:

                sql = "update order_2 set ps_record = '%s' where order_id='%s' " % (1, orderid)

                while 1:
                    try:
                        mysql_tengxun.mysql_db(sql)
                        break
                    except:
                        time.sleep(1)
                        print('update_order2_error')
                        break

                sql = "insert into ps_record set creat_time='%s',ps_time='%s',orderid='%s',sf_orderid='%s',platform='%s',order_num='%s',sf_status='%s'" % (
                    datetime.datetime.now(), datetime.datetime.now(), orderid, sf_id, platform, order_num, 1)
                while 1:
                    try:
                        mysql_tengxun.mysql_db(sql)
                        print('insert_one_data')
                        break
                    except:
                        time.sleep(1)
                        print('insert___date__error')
                        break

    # 声明全局变量
    global t1
    # 创建并初始化线程
    t1 = threading.Timer(3, creat_order)
    # 启动线程
    t1.start()


def get_status():

    print('获取订单状态，配送员坐标')
    now_time = datetime.datetime.now() + datetime.timedelta(hours=-3)

    sql = "SELECT * FROM ps_record WHERE platform='%s' and sf_taketime != '%s' and sf_status !='%s' and sf_status !='%s' and creat_time>'%s'" % ('饿了么',
    'Null', 2, 17, now_time)

    while 1:
        try:
            data_sql = mysql_tengxun.mysql_getdata(sql)
            break

        except:
            time.sleep(1)
            print('get jiroudone data error')


    if data_sql:

        for data in data_sql:

            timestamp = int(time.time())
            jichu_url = "/open/api/external/getorderstatus?"

            dict_str = {
                "order_id": str(data[5]),
                "order_type": "1",
                "dev_id": "1547215874",
                "push_time": str(timestamp)
            }
            sf_data = do_sf(dict_str, jichu_url)

            sf_status = jsonpath.jsonpath(sf_data, '$..order_status')[0]
            sql = "update ps_record set sf_status = '%s' where orderid='%s' " % (sf_status, data[2])

            while 1:
                try:
                    mysql_tengxun.mysql_db(sql)
                    print('update_sf_status')
                    break
                except:
                    time.sleep(1)
                    print('update_order2_error')
                    break

            if sf_status == 15:
                timestamp = int(time.time())
                jichu_url = "/open/api/external/riderlatestposition?"

                dict_str = {
                    "order_id": str(data[5]),
                    "order_type": "1",
                    "dev_id": "1547215874",
                    "push_time": str(timestamp)
                }
                sf_data = do_sf(dict_str, jichu_url)
                print(sf_data)
                rider_lng = jsonpath.jsonpath(sf_data, '$..rider_lng')[0]
                rider_lat = jsonpath.jsonpath(sf_data, '$..rider_lat')[0]

                sql = "update ps_record set sf_lng = '%s',sf_lat='%s',sf_upload_time='%s' where orderid='%s' " % (
                rider_lng, rider_lat, datetime.datetime.now(), data[2])

                while 1:
                    try:
                        mysql_tengxun.mysql_db(sql)
                        print('update_sf_lng')
                        break
                    except:
                        time.sleep(1)
                        print('update_order2_error')
                        break
    # 去时刻查看棋手位置和配送状态，并回传
    global t3

    t3 = threading.Timer(10, get_status)
    # 启动线程
    t3.start()

def send_status():

    print('去给平台回传配送员位置')
    now_time = datetime.datetime.now() + datetime.timedelta(hours=-3)

    sql = "SELECT * FROM ps_record WHERE platform='%s' and sf_taketime != '%s' and sf_status !='%s' and sf_status !='%s' and creat_time>'%s' and sf_upload_time!='%s'" % ('饿了么',
    'Null', 2, 17, now_time,'Null')

    while 1:
        try:
            data_sql = mysql_tengxun.mysql_getdata(sql)
            break

        except:
            time.sleep(1)
            print('get ps_record_ data error')

    if data_sql:

        for data in data_sql:
            if (datetime.datetime.now()-data[13]).seconds<60:

                if data[9]=='饿了么':

                    timestamp = int(time.time())

                    orderid = data[2]

                    action = "eleme.order.selfDeliveryLocationSync"

                    params = {

                            "shopId": 155852887,
                            "orderId": data[2],
                            "locationInfo": {
                                "latitude": data[12],
                                "longitude": data[11],
                                "altitude": 120.34,
                                "utc": timestamp
                            }

                    }

                    do_ele(orderid, action, params)

    # 去时刻查看棋手位置和配送状态，并回传

    global t4

    t4 = threading.Timer(10, send_status)
    # 启动线程
    t4.start()

if __name__ == "__main__":
    # 创建并初始化线程,创建订单
    t1 = threading.Timer(3, creat_order)
    # 启动线程
    t1.start()

    # 到时间了就取消订单
    t2 = threading.Timer(3, cancel_order)
    # 启动线程
    t2.start()

    # 去时刻查看棋手位置和配送状态，并回传
    t3 = threading.Timer(10, get_status)
    # 启动线程
    t3.start()

    # 去时刻查看棋手位置和配送状态，并回传
    t4 = threading.Timer(10, send_status)
    # 启动线程
    t4.start()