import datetime
import time
import mysql_tengxun
import do_allps
import jsonpath
import threading

def cancel_sf():

    print("进来查顺丰")
    now_time = datetime.datetime.now() + datetime.timedelta(hours=-3)

    sql = "SELECT * FROM ps_record WHERE sf_taketime is NULL and cancel_time is NULL and sf_donetime is NULL and creat_time > '%s'" % (now_time)

    while 1:
        try:
            data_sql = mysql_tengxun.mysql_getdata(sql)
            break

        except:
            time.sleep(1)
            print('get ps_record_cancel_order_ data error')
            continue

    if data_sql:

        for data in data_sql:

            if data[9]=='美团':
                cancel_long=mt_cancel_long
            else:
                cancel_long=ele_cancel_long


            if data[7]!=None or data[19]!=None or (data[7]==None and data[19]==None and 3600>(datetime.datetime.now()-data[1]).seconds>(cancel_long-5)):

                print(data[7],data[19],cancel_long,"取消顺丰订单",data[9],data[10],data[1],(datetime.datetime.now()-data[1]).seconds)

                timestamp = int(time.time())

                jichu_url = "/open/api/external/cancelorder?"

                dict_str = {
                    "order_id": data[5],
                    "order_type": "1",
                    "dev_id": "1547215874",
                    "push_time": str(timestamp)
                }

                data_json = do_allps.do_sf(dict_str, jichu_url)
                error_code = jsonpath.jsonpath(data_json, '$..error_code')[0]

                if error_code == 0:

                    print('取消顺丰配送成功',data[9],data[10])
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

    global t1
    # 创建并初始化线程,创建订单
    t1 = threading.Timer(1, cancel_sf)
    # 启动线程
    t1.start()

def cancel_dd():

    print("进来查达达")
    now_time = datetime.datetime.now() + datetime.timedelta(hours=-3)

    sql = "SELECT * FROM ps_record WHERE dd_fadantime is not NULL and dd_taketime is NULL and dd_canceltime is NULL and dd_donetime is NULL and creat_time > '%s'" % (now_time)

    while 1:
        try:
            data_sql = mysql_tengxun.mysql_getdata(sql)
            break

        except:
            time.sleep(1)
            print('get ps_record_cancel_order_ data error')
            continue

    if data_sql:
        for data in data_sql:

            if data[9] == '美团':
                cancel_long = mt_cancel_long
            else:
                cancel_long = ele_cancel_long

            if data[7] != None or data[6] != None or (data[7] == None and data[6] == None and 3600>(datetime.datetime.now()-data[1]).seconds>(cancel_long-5)):

                print(data[7],data[6],cancel_long,"取消达达订单",data[9],data[10],(datetime.datetime.now()-data[1]).seconds)

                url = "/api/order/formalCancel"

                body = {
                    "order_id": data[2],
                    "cancel_reason_id": "1",
                }

                data_json = do_allps.do_dada(url, body)

                print(data_json)

                dd_status = jsonpath.jsonpath(data_json, '$..status')[0]

                if dd_status == 'success':

                    print('取消达达配送成功',data[9],data[10])

                    sql = "update ps_record set dd_canceltime = '%s' where orderid='%s' " % (
                        datetime.datetime.now(), data[2])

                    while 1:
                        try:
                            mysql_tengxun.mysql_db(sql)
                            break
                        except:
                            time.sleep(1)
                            print('update_ps_record_error')
                            continue

    global t2
    # 创建并初始化线程,创建订单
    t2 = threading.Timer(1, cancel_dd)
    # 启动线程
    t2.start()

def cancel_mt():

    print("进来查美团")
    now_time = datetime.datetime.now() + datetime.timedelta(hours=-3)

    sql = "SELECT * FROM ps_record WHERE platform='%s' and mt_canceltime is NULL and creat_time > '%s'" % ('美团',now_time)

    while 1:
        try:
            data_sql = mysql_tengxun.mysql_getdata(sql)
            break

        except:
            time.sleep(1)
            print('get ps_record_cancel_order_ data error')
            continue

    if data_sql:

        for data in data_sql:

            if data[6] != None or data[19] != None:

                print('取消美团订单',data[9],data[10])

                url = 'https://api-open-cater.meituan.com/waimai/order/cancelZbLogisticsByWmOrderId'
                biz = {
                    "detailContent": "noneed",
                    "orderId": data[2],
                    "reasonCode": "1"
                }
                data_json = do_allps.do_mt(url, biz)

                print(data_json)

                error_code = jsonpath.jsonpath(data_json, '$..code')[0]

                if error_code == 'OP_SUCCESS':

                    print('取消美团配送成功',data[9],data[10])

                    sql = "update ps_record set  mt_canceltime= '%s' where orderid='%s' " % (
                        datetime.datetime.now(), data[2])

                    while 1:
                        try:
                            mysql_tengxun.mysql_db(sql)
                            break
                        except:
                            time.sleep(1)
                            print('update_sf_taketime_error')
                            continue

    global t3
    # 创建并初始化线程,创建订单
    t3 = threading.Timer(1, cancel_mt)
    # 启动线程
    t3.start()

def get_cancel_long():


    global mt_cancel_long
    global ele_cancel_long

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
            mt_cancel_long = int(data[1]) * 60
            ele_cancel_long= int(data[2]) * 60


    global t4
    # 去获取取消时间
    t4 = threading.Timer(30, get_cancel_long)
    # 启动线程
    t4.start()

if __name__=="__main__":

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
            mt_cancel_long = int(data[1]) * 60
            ele_cancel_long= int(data[2]) * 60

    # 创建并初始化线程,创建订单
    t1 = threading.Timer(1, cancel_sf)
    # 启动线程
    t1.start()

    # 创建并初始化线程,创建订单
    t2 = threading.Timer(1, cancel_dd)
    # 启动线程
    t2.start()

    # 创建并初始化线程,创建订单
    t3 = threading.Timer(1, cancel_mt)
    # 启动线程
    t3.start()

    # 去获取取消时间
    t4 = threading.Timer(30, get_cancel_long)
    # 启动线程
    t4.start()
