# -*- coding:utf-8 -*-
import datetime
import mysql_tengxun
import time
import jsonpath
import threading
import do_allps


def get_order(platform,order_id):

    now_time = datetime.datetime.now() + datetime.timedelta(hours=-3)

    sql = "SELECT * FROM order_2 WHERE order_id='%s' and platform = '%s' and creat_time > '%s'  and dingdan_status!='%s' and peisongy='%s' and ps_record is NULL" % (order_id,
        platform, now_time, -4, 'None')

    while 1:
        try:
            data_sql = mysql_tengxun.mysql_getdata(sql)
            break

        except:
            time.sleep(1)
            print('get jiroudone data error')

    return data_sql

def get_cancel_long():

    #美团
    global  cancel_long

    sql = "SELECT * FROM cancel_long"

    while 1:
        try:
            data_sql = mysql_tengxun.mysql_getdata(sql)
            break

        except:
            time.sleep(1)
            print('get ps_record_cancel_long data error')

    for data in data_sql:
        hours_big=int(data[3].split(',')[1])
        hours_small=int(data[3].split(',')[0])
        if hours_big>int(datetime.datetime.now().strftime('%H'))>hours_small:
            cancel_long = int(data[1]) * 60

    global t5
    # 去时刻查看棋手位置和配送状态，并回传
    t5 = threading.Timer(30, get_cancel_long)
    # 启动线程
    t5.start()

def cancel_sf():

    print("取消顺丰订单检查")

    now_time = datetime.datetime.now() + datetime.timedelta(hours=-3)

    sql = "SELECT * FROM ps_record WHERE  sf_taketime is NULL  and platform='%s' and mt_ordertime is not NULL and cancel_time is NULL and creat_time > '%s'" % ('美团',now_time)

    while 1:
        try:
            data_sql = mysql_tengxun.mysql_getdata(sql)
            break

        except:
            time.sleep(1)
            print('get ps_record_cancel_order_ data error')
            break

    if data_sql:

        for data in data_sql:

            #超过发顺丰时间了就取消顺丰
            if (datetime.datetime.now() - data[14]).seconds > cancel_long-5:

                timestamp = int(time.time())

                jichu_url = "/open/api/external/cancelorder?"

                dict_str = {
                    "order_id": data[5],
                    "order_type": "1",
                    "dev_id": "1547215874",
                    "push_time": str(timestamp)
                }

                data_json = do_allps.do_sf(dict_str, jichu_url)
                error_code=jsonpath.jsonpath(data_json, '$..error_code')[0]

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

            if (datetime.datetime.now() - data[14]).seconds < cancel_long-5:

                timestamp = int(time.time())
                jichu_url = "/open/api/external/getorderstatus?"

                dict_str = {
                    "order_id": data[5],
                    "order_type": "1",
                    "dev_id": "1547215874",
                    "push_time": str(timestamp)
                }

                data_json=do_allps.do_sf(dict_str, jichu_url)

                error_code=jsonpath.jsonpath(data_json, '$..error_code')[0]
                status_code=jsonpath.jsonpath(data_json, '$..order_status')[0]
                rider_name=jsonpath.jsonpath(data_json, '$..rider_name')[0]
                rider_phone=jsonpath.jsonpath(data_json, '$..rider_phone')[0]

                if error_code == 0:

                    #这里的订单状态是指1，2，17分别对应，发单，取消，完成
                    if status_code != 1 and status_code != 2 and status_code!=17:

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

                        sql = "update ps_record set sf_taketime = '%s',sf_status='%s',rider_name='%s',rider_phone='%s' where orderid='%s'" % (datetime.datetime.now(), status_code,rider_name,rider_phone, data[2])

                        while 1:
                            try:
                                mysql_tengxun.mysql_db(sql)
                                break
                            except:
                                time.sleep(1)
                                print('update_sf_taketime_error')
                                continue


    # 声明全局变量
    global t2
    # 创建并初始化线程
    t2 = threading.Timer(3, cancel_sf)
    # 启动线程
    t2.start()

def cancel_mt():

    print('取消美团订单检查')

    now_time = datetime.datetime.now() + datetime.timedelta(hours=-3)

    sql = "SELECT * FROM ps_record WHERE  sf_taketime is not NULL and mt_ordertime is not NULL and mt_canceltime is NULL and platform='%s' and creat_time > '%s'" % ('美团',
        now_time)
    while 1:
        try:
            data_sql = mysql_tengxun.mysql_getdata(sql)
            break

        except:
            time.sleep(1)
            print('get ps_record_cancel_mt_ data error')
            break

    for data in data_sql:

        if (datetime.datetime.now() - data[14]).seconds < cancel_long:

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

                print('取消配送成功')

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

                # 美团同步配送信息
                timestamp = int(time.time())
                url = 'https://api-open-cater.meituan.com/waimai/order/riderPosition'

                biz = {
                    "thirdLogisticsId": 10017,
                    "courierName": "rider",
                    "thirdCarrierId": "3368153620852828000",
                    "orderId": data[2],
                    "latitude": "39.904979",
                    "courierPhone": data[17],
                    "logisticsStatus": 10,
                    "backFlowTime": timestamp,
                    "longitude": "116.458171"
                }

                data_response = do_allps.do_mt(url, biz)

    # 声明全局变量
    global t6
    # 创建并初始化线程
    t6 = threading.Timer(3, cancel_mt)
    # 启动线程
    t6.start()

def creat_order():

    print('进来发单了')
    orderid="18488792089812656"
    order_data = get_order('美团',orderid)

    if order_data:

        for data in order_data:
            print(data)
            timestamp = int(time.time())

            jichu_url = "/open/api/external/createorder?"

            # 转换为时间戳
            order_time = str(data[1])
            order_time = time.strptime(order_time, "%Y-%m-%d %H:%M:%S")
            order_time = int(time.mktime(order_time))
            # total_price 转为分
            total_price = int(data[8] * 100)
            # 经纬度转换一下
            costomer_lng = str(data[14] / 1000000)
            costomer_lat = str(data[13] / 1000000)

            dict_str = {
                "shop_id": "6250508608337",
                "shop_order_id": str(data[9]),
                "dev_id": "1547215874",
                "order_source": "1",
                "order_sequence": str(data[6]),
                "pay_type": "1",
                "lbs_type": "2",
                "order_time": str(order_time),
                "is_appoint": "0",
                "is_person_direct": "0",
                "push_time": str(timestamp),
                "version": "17",
                "is_insured": "0",
                "receive": {
                    "user_name": str(data[19]),
                    "user_phone": str(data[3]),
                    "user_address": str(data[2]),
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

            data_json = do_allps.do_sf(dict_str, jichu_url)
            print(data_json)
            error_code = jsonpath.jsonpath(data_json, '$..error_code')[0]
            sf_id = jsonpath.jsonpath(data_json, '$..sf_order_id')[0]
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
                    datetime.datetime.now(), datetime.datetime.now(), orderid, sf_id, data[4], data[6], 1)
                while 1:
                    try:
                        mysql_tengxun.mysql_db(sql)
                        print('insert_one_data')
                        break
                    except:
                        time.sleep(1)
                        print('insert___date__error')
                        continue

                #去拿美团的下单时间
                url = 'https://api-open-cater.meituan.com/waimai/order/queryById'

                biz = {"orderId": orderid}

                data_json = do_allps.do_mt(url, biz)

                timeStamp = jsonpath.jsonpath(data_json, '$..cTime')[0]

                timeArray = time.localtime(timeStamp)

                now_time = datetime.datetime.strptime(time.strftime("%Y-%m-%d %H:%M:%S", timeArray),"%Y-%m-%d %H:%M:%S")

                sql = "update ps_record set mt_ordertime = '%s' where orderid='%s' " % (now_time, orderid)

                while 1:
                    try:
                        mysql_tengxun.mysql_db(sql)
                        break
                    except:
                        time.sleep(1)
                        print('update_order2_error')
                        continue

    # 声明全局变量
    global t1
    # 创建并初始化线程
    t1 = threading.Timer(3, creat_order)
    # 启动线程
    t1.start()


def get_status():

    print('获取订单状态，配送员坐标')
    now_time = datetime.datetime.now() + datetime.timedelta(hours=-3)

    sql = "SELECT * FROM ps_record WHERE platform='%s' and sf_taketime != '%s' and sf_status !='%s' and sf_status !='%s' and creat_time>'%s' and sf_upload_time!='%s'" % ('美团',
    'Null', 2, 17, now_time,'Null')

    while 1:
        try:
            data_sql = mysql_tengxun.mysql_getdata(sql)
            break

        except:
            time.sleep(1)
            print('get ps_record_getstatus_data error')


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
            sf_data = do_allps.do_sf(dict_str, jichu_url)

            sf_status = jsonpath.jsonpath(sf_data, '$..order_status')[0]

            print(sf_status)

            sql = "update ps_record set sf_status = '%s' where orderid='%s' " % (sf_status, data[2])

            while 1:
                try:
                    mysql_tengxun.mysql_db(sql)
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
                sf_data = do_allps.do_sf(dict_str, jichu_url)
                print(sf_data)
                rider_lng = jsonpath.jsonpath(sf_data, '$..rider_lng')[0]
                rider_lat = jsonpath.jsonpath(sf_data, '$..rider_lat')[0]

                sql = "update ps_record set sf_lng = '%s',sf_lat='%s',sf_upload_time='%s' where orderid='%s' " % (
                rider_lng, rider_lat, datetime.datetime.now(), data[2])

                while 1:
                    try:
                        mysql_tengxun.mysql_db(sql)
                        break
                    except:
                        time.sleep(1)
                        print('update_order2_error')
                        break

    global t3
    # 去时刻查看棋手位置和配送状态，并回传
    t3 = threading.Timer(20, get_status)
    # 启动线程
    t3.start()

def send_status():

    print('去给平台回传配送员位置')
    #美团顺丰配送状态对应关系
    li=[[10,10],[12,15],[15,20],[17,40]]

    now_time = datetime.datetime.now() + datetime.timedelta(hours=-3)

    sql = "SELECT * FROM ps_record WHERE platform='%s' and sf_taketime != '%s' and sf_donetime is NULL and sf_status !='%s' and creat_time>'%s' and sf_upload_time!='%s'" % (
        '美团', 'Null', 2, now_time, 'Null')

    while 1:
        try:
            data_sql = mysql_tengxun.mysql_getdata(sql)
            break

        except:
            time.sleep(1)
            print('get ps_record_ data error')

    print(data_sql)
    if data_sql:
        print('jinlaihuichuan')
        for data in data_sql:
            if (datetime.datetime.now()-data[13]).seconds<60:

                if data[9]=='美团':

                    if data[8] == 17:

                        # 美团同步配送信息
                        timestamp = int(time.time())
                        url = 'https://api-open-cater.meituan.com/waimai/order/riderPosition'

                        biz = {
                            "thirdLogisticsId": 10017,
                            "courierName": "rider",
                            "thirdCarrierId": "3368153620852828000",
                            "orderId": data[2],
                            "latitude": "39.904979",
                            "courierPhone": data[17],
                            "logisticsStatus": 40,
                            "backFlowTime": timestamp,
                            "longitude": "116.458171"
                        }

                        print(biz)

                        data_response = do_allps.do_mt(url, biz)
                        print(data_response)

                        sql = "update ps_record set sf_donetime = '%s' where orderid='%s' " % (
                        datetime.datetime.now(), data[2])

                        while 1:
                            try:
                                mysql_tengxun.mysql_db(sql)
                                break
                            except:
                                time.sleep(1)
                                print('update_order2_error')
                                continue

                    else:
                        for i in range(len(li)):
                            if li[i][0]==data[8]:
                                dingdan_status=li[i][1]
                        print(dingdan_status)
                        # 美团同步配送信息
                        timestamp = int(time.time())
                        url = 'https://api-open-cater.meituan.com/waimai/order/riderPosition'

                        biz = {
                            "thirdLogisticsId": 10017,
                            "courierName": "rider",
                            "thirdCarrierId": "3368153620852828000",
                            "orderId": data[2],
                            "latitude": "39.904979",
                            "courierPhone": data[17],
                            "logisticsStatus": dingdan_status,
                            "backFlowTime": timestamp,
                            "longitude": "116.458171"
                        }

                        print(biz)

                        data_response = do_allps.do_mt(url, biz)
                        print(data_response)

    global t4
    # 去时刻查看棋手位置和配送状态，并回传
    t4 = threading.Timer(20, send_status)
    # 启动线程
    t4.start()

if __name__ == "__main__":

    cancel_long=480

    sql = "SELECT * FROM cancel_long"

    while 1:
        try:
            data_sql = mysql_tengxun.mysql_getdata(sql)
            break

        except:
            time.sleep(1)
            print('get ps_record_cancel_long data error')

    for data in data_sql:
        hours_big = int(data[3].split(',')[1])
        hours_small = int(data[3].split(',')[0])
        if hours_big > int(datetime.datetime.now().strftime('%H')) > hours_small:
            cancel_long = int(data[1]) * 60

    # 创建并初始化线程,创建订单
    t1 = threading.Timer(3, creat_order)
    # 启动线程
    t1.start()

    # 到时间了就取消订单
    t2 = threading.Timer(3, cancel_sf)
    # 启动线程
    t2.start()

    # 去时刻查看棋手位置和配送状态，并回传
    t3 = threading.Timer(20, get_status)
    # 启动线程
    t3.start()

    # 去时刻查看棋手位置和配送状态，并回传
    t4 = threading.Timer(20, send_status)
    # 启动线程
    t4.start()

    # 去获取取消时间
    t5 = threading.Timer(30, get_cancel_long)
    # 启动线程
    t5.start()

    # 去获取取消时间
    t6 = threading.Timer(2, cancel_mt)
    # 启动线程
    t6.start()