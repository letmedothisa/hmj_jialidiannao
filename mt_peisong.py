# -*- coding:utf-8 -*-
import datetime
import mysql_tengxun
import time
import jsonpath
import threading
import do_allps


def get_mtdingda_time():

    now_time = datetime.datetime.now() + datetime.timedelta(hours=-3)

    data_sql=[]

    sql = "SELECT * FROM ps_record WHERE platform='%s' and mt_ordertime is NULL and creat_time > '%s'" % ('美团',now_time)

    while 1:
        try:
            data_sql = mysql_tengxun.mysql_getdata(sql)
            break

        except:
            time.sleep(1)
            print('get jiroudone data error')
            continue

    if data_sql:

        for data in data_sql:

            orderid=data[2]

            url = 'https://api-open-cater.meituan.com/waimai/order/queryById'

            biz = {"orderId": orderid}

            data_json = do_allps.do_mt(url, biz)

            print(data_json)

            error_code = jsonpath.jsonpath(data_json, '$..code')[0]

            if error_code == 'OP_SUCCESS':

                timeStamp = jsonpath.jsonpath(data_json, '$..cTime')[0]

                timeArray = time.localtime(timeStamp)

                now_time = datetime.datetime.strptime(time.strftime("%Y-%m-%d %H:%M:%S", timeArray), "%Y-%m-%d %H:%M:%S")

                sql = "update ps_record set mt_ordertime = '%s',creat_time='%s' where orderid='%s' " % (now_time,now_time,orderid)

                while 1:
                    try:
                        mysql_tengxun.mysql_db(sql)
                        break
                    except:
                        time.sleep(1)
                        print('update_order2_error')
                        continue

    global t1
    # 去时刻查看棋手位置和配送状态，并回传
    t1 = threading.Timer(3, get_mtdingda_time)
    # 启动线程
    t1.start()


def send_status():

    print('去给美团回传配送员位置')

    # 美团顺丰配送状态对应关系

    now_time = datetime.datetime.now() + datetime.timedelta(hours=-3)

    sql = "SELECT * FROM ps_record WHERE platform='%s' and upload_done is NULL and (sf_taketime is not NULL or dd_taketime is not NULL) and creat_time>'%s'"%('美团',now_time)


    while 1:
        try:
            data_sql = mysql_tengxun.mysql_getdata(sql)
            break

        except:
            time.sleep(1)
            print('get ps_record_data error')
            continue

    if data_sql:

        for data in data_sql:

            # 如果还没有拿到经纬度信息

            if data[11] == None:

                timestamp = int(time.time())
                url = 'https://api-open-cater.meituan.com/waimai/order/riderPosition'

                biz = {
                    "thirdLogisticsId": 10017,
                    "courierName": "rider",
                    "thirdCarrierId": "3368153620852828000",
                    "orderId": data[2],
                    "latitude": "39.904979",
                    "courierPhone": data[17],
                    "logisticsStatus": 20,
                    "backFlowTime": timestamp,
                    "longitude": "116.458171"
                }

                data_json = do_allps.do_mt(url, biz)

                error_code = jsonpath.jsonpath(data_json, '$..code')[0]

                if error_code != 'OP_SUCCESS':
                    print(data_json, data[9], data[10], data[11], data[18])

            # 如果拿到了经纬度信息
            elif data[11] != None:

                # 顺丰没有完成
                if data[18] == None:

                    timestamp = int(time.time())

                    url = 'https://api-open-cater.meituan.com/waimai/order/riderPosition'

                    biz = {
                        "thirdLogisticsId": 10017,
                        "courierName": "rider",
                        "thirdCarrierId": "3368153620852828000",
                        "orderId": data[2],
                        "latitude": data[12],
                        "courierPhone": data[17],
                        "logisticsStatus": 20,
                        "backFlowTime": timestamp,
                        "longitude": data[11]
                    }

                    data_json = do_allps.do_mt(url, biz)

                    error_code = jsonpath.jsonpath(data_json, '$..code')[0]

                    if error_code != 'OP_SUCCESS':
                        print(data_json, data[9], data[10], data[11], data[18])

                else:
                    timestamp = int(time.time())

                    url = 'https://api-open-cater.meituan.com/waimai/order/riderPosition'

                    biz = {
                        "thirdLogisticsId": 10017,
                        "courierName": "rider",
                        "thirdCarrierId": "3368153620852828000",
                        "orderId": data[2],
                        "latitude": data[12],
                        "courierPhone": data[17],
                        "logisticsStatus": 40,
                        "backFlowTime": timestamp,
                        "longitude": data[11]
                    }

                    data_json = do_allps.do_mt(url, biz)

                    error_code = jsonpath.jsonpath(data_json, '$..code')[0]

                    if error_code != 'OP_SUCCESS':
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

            # 这里是达达有回传坐标
            elif data[22] != None:

                # 这里是达达没有完成
                if data[24] == None:

                    timestamp = int(time.time())

                    url = 'https://api-open-cater.meituan.com/waimai/order/riderPosition'

                    biz = {
                        "thirdLogisticsId": 10017,
                        "courierName": "rider",
                        "thirdCarrierId": "3368153620852828000",
                        "orderId": data[2],
                        "latitude": data[23],
                        "courierPhone": data[17],
                        "logisticsStatus": 20,
                        "backFlowTime": timestamp,
                        "longitude": data[22]
                    }

                    data_json = do_allps.do_mt(url, biz)

                    error_code = jsonpath.jsonpath(data_json, '$..code')[0]

                    if error_code != 'OP_SUCCESS':
                        print(data_json, data[9], data[10], data[11], data[18])


                else:

                    timestamp = int(time.time())

                    url = 'https://api-open-cater.meituan.com/waimai/order/riderPosition'

                    biz = {
                        "thirdLogisticsId": 10017,
                        "courierName": "rider",
                        "thirdCarrierId": "3368153620852828000",
                        "orderId": data[2],
                        "latitude": data[23],
                        "courierPhone": data[17],
                        "logisticsStatus": 40,
                        "backFlowTime": timestamp,
                        "longitude": data[22]
                    }

                    data_json = do_allps.do_mt(url, biz)

                    error_code = jsonpath.jsonpath(data_json, '$..code')[0]

                    if error_code != 'OP_SUCCESS':
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
    global t2
    # 去获取取消时间
    t2 = threading.Timer(3, send_status)
    # 启动线程
    t2.start()

if __name__ == "__main__":

    # 去时刻查看棋手位置和配送状态，并回传
    t1 = threading.Timer(3, get_mtdingda_time)
    # 启动线程
    t1.start()

    # 到时间了就取消订单
    t2 = threading.Timer(3, send_status)
    # 启动线程
    t2.start()
