# -*- coding:utf-8 -*-
import datetime
import mysql_tengxun
import time
import jsonpath
import threading
import do_allps


def creat_ele():

    print('饿了么发单检查')

    now_time = datetime.datetime.now() + datetime.timedelta(hours=-3)

    sql = "SELECT * FROM ps_record where platform ='%s' and sf_taketime is NULL and ele_fadantime is NULL and  dd_taketime is NULL and creat_time>'%s'" % ('饿了么',now_time)

    while 1:
        try:
            data_sql = mysql_tengxun.mysql_getdata(sql)
            break

        except:
            time.sleep(1)
            print('get jiroudone data error')

    if data_sql:

        for data in data_sql:

            if (datetime.datetime.now()-data[1]).seconds>cancel_long:


                action = "eleme.order.callDelivery"

                params = {
                    "orderId": data[2]
                }

                data_json = do_allps.do_ele(action, params)

                print(data_json,data[9],data[10])

                error_code = jsonpath.jsonpath(data_json, '$..error')[0]

                if error_code==None:

                    sql = "update ps_record set ele_fadantime = '%s' where orderid='%s'" % (datetime.datetime.now(),data[2])

                    while 1:
                        try:
                            mysql_tengxun.mysql_db(sql)
                            break
                        except:
                            time.sleep(1)
                            print('update_sf_taketime_error')
                            continue
    global t1
    # 去获取取消时间
    t1 = threading.Timer(3, creat_ele)
    # 启动线程
    t1.start()

def send_status():

    print('去给平台回传配送员位置')

    now_time = datetime.datetime.now() + datetime.timedelta(hours=-3)

    sql = "SELECT * FROM ps_record WHERE platform='%s' and upload_done is NULL and ele_fadantime is NULL and (sf_taketime is not NULL or dd_taketime is not NULL) and creat_time>'%s'"%('饿了么',now_time)

    while 1:
        try:
            data_sql = mysql_tengxun.mysql_getdata(sql)
            break

        except:
            time.sleep(1)
            print('get ps_record_ data error')
            continue

    if data_sql:

        for data in data_sql:

            if data[11]==None:

                action = "eleme.order.selfDeliveryStateSync"

                params = {

                    "shopId": 155852887,
                    "stateInfo": {
                        "orderId": data[2],
                        "distributorId": 201,
                        "state": "DELIVERY_START",
                    }

                }
                data_json = do_allps.do_ele(action, params)
                error_code = jsonpath.jsonpath(data_json, '$..error')[0]
                if error_code!=None:
                    print(data_json,data[9],data[10],data[11],data[18])

            #这里是顺丰有回传坐标
            if data[11] !=None:

                action = "eleme.order.selfDeliveryStateSync"

                params = {

                    "shopId": 155852887,
                    "stateInfo": {
                        "orderId": data[2],
                        "distributorId": 201,
                        "state": "DELIVERY_START",
                    }

                }
                data_json = do_allps.do_ele(action, params)
                error_code = jsonpath.jsonpath(data_json, '$..error')[0]
                if error_code!=None:
                    print(data_json,data[9],data[10],data[11],data[18])

                #顺丰没有完成
                if data[18]==None:

                    timestamp = int(time.time())

                    action = "eleme.order.selfDeliveryLocationSync"

                    params = {

                            "shopId": 155852887,
                            "orderId": data[2],
                            "locationInfo": {
                                "latitude": data[12],
                                "longitude": data[11],
                                "altitude": 50.34,
                                "utc": timestamp
                            }

                    }

                    data_json = do_allps.do_ele(action, params)
                    error_code = jsonpath.jsonpath(data_json, '$..error')[0]
                    if error_code != None:
                        print(data_json, data[9], data[10], data[11], data[18])

                else:

                    action = "eleme.order.selfDeliveryStateSync"

                    params = {

                        "shopId": 155852887,
                        "stateInfo": {
                            "orderId": data[2],
                            "distributorId": 201,
                            "state": "DELIVERY_COMPLETE",
                        }

                    }

                    data_json = do_allps.do_ele(action, params)
                    error_code = jsonpath.jsonpath(data_json, '$..error')[0]
                    if error_code != None:
                        print(data_json, data[9], data[10], data[11], data[18])
                    else:
                        sql = "update ps_record set upload_done='%s' where orderid='%s'" % (
                            1, data[2])

                        while 1:
                            try:
                                mysql_tengxun.mysql_db(sql)
                                break
                            except:
                                time.sleep(1)
                                print('update_sf_taketime_error')
                                continue

            #这里是达达有回传坐标
            elif data[22]!=None:

                #这里是达达没有完成
                if data[24] == None:

                    timestamp = int(time.time())

                    action = "eleme.order.selfDeliveryLocationSync"

                    params = {

                        "shopId": 155852887,
                        "orderId": data[2],
                        "locationInfo": {
                            "latitude": data[23],
                            "longitude": data[22],
                            "altitude": 50.34,
                            "utc": timestamp
                        }

                    }

                    data_json = do_allps.do_ele(action, params)
                    error_code = jsonpath.jsonpath(data_json, '$..error')[0]
                    if error_code != None:
                        print(action,data_json, data[9], data[10])

                    action = "eleme.order.selfDeliveryStateSync"

                    params = {

                        "shopId": 155852887,
                        "stateInfo": {
                            "orderId": data[2],
                            "distributorId": 201,
                            "state": "DELIVERY_START",
                        }

                    }

                    data_json = do_allps.do_ele(action, params)
                    error_code = jsonpath.jsonpath(data_json, '$..error')[0]
                    if error_code != None:
                        print(action,data_json, data[9], data[10])

                else:
                    action = "eleme.order.selfDeliveryStateSync"

                    params = {

                        "shopId": 155852887,
                        "stateInfo": {
                            "orderId": data[2],
                            "distributorId": 201,
                            "state": "DELIVERY_COMPLETE",
                        }

                    }

                    data_json = do_allps.do_ele(action, params)
                    error_code = jsonpath.jsonpath(data_json, '$..error')[0]
                    if error_code != None:
                        print(action,data_json, data[9], data[10])
                    else:
                        sql = "update ps_record set upload_done='%s' where orderid='%s'" % (
                        1, data[2])

                        while 1:
                            try:
                                mysql_tengxun.mysql_db(sql)
                                break
                            except:
                                time.sleep(1)
                                print('update_sf_taketime_error')
                                continue

    global t2
    # 去获取取消时间
    t2 = threading.Timer(3, send_status)
    # 启动线程
    t2.start()

def get_cancel_long():


    global cancel_long

    sql = "SELECT * FROM cancel_long"

    while 1:
        try:
            data_sql = mysql_tengxun.mysql_getdata(sql)
            break

        except:
            time.sleep(1)
            print('get ps_record_cancel_long data error')
            continue

    for data in data_sql:
        hours_big = int(data[3].split(',')[1])
        hours_small = int(data[3].split(',')[0])
        if hours_big > int(datetime.datetime.now().strftime('%H')) >= hours_small:
            cancel_long = int(data[2]) * 60

    print('获取取消时间',cancel_long)

    global t3
    # 去获取取消时间
    t3 = threading.Timer(30, get_cancel_long)
    # 启动线程
    t3.start()

if __name__=='__main__':

    sql = "SELECT * FROM cancel_long"

    while 1:
        try:
            data_sql = mysql_tengxun.mysql_getdata(sql)
            break

        except:
            time.sleep(1)
            print('get ps_record_cancel_long data error')
            continue

    for data in data_sql:
        hours_big = int(data[3].split(',')[1])
        hours_small = int(data[3].split(',')[0])
        if hours_big > int(datetime.datetime.now().strftime('%H')) >= hours_small:
            cancel_long = int(data[2]) * 60


    # 去获取取消时间
    t1 = threading.Timer(3, creat_ele)
    # 启动线程
    t1.start()

    # 去获取取消时间
    t2 = threading.Timer(3, send_status)
    # 启动线程
    t2.start()

    # 去获取取消时间
    t3 = threading.Timer(30, get_cancel_long)
    # 启动线程
    t3.start()