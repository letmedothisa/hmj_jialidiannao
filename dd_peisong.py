# -*- coding:utf-8 -*-
import datetime
import mysql_tengxun
import time
import jsonpath
import do_allps
import threading

def get_cancel_long():

    print("获取取消时长")
    global  cancel_long

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
        hours_big=int(data[3].split(',')[1])
        hours_small=int(data[3].split(',')[0])
        if hours_big>int(datetime.datetime.now().strftime('%H'))>hours_small:
            cancel_long = int(data[1]) * 60

    global t5
    # 去时刻查看棋手位置和配送状态，并回传
    t5 = threading.Timer(30, get_cancel_long)
    # 启动线程
    t5.start()


def get_order():

    now_time = datetime.datetime.now() + datetime.timedelta(minutes=-1)

    sql = "SELECT * FROM order_2 where creat_time > '%s' and ps_record ='%s' and ps_dd is NULL" % (now_time,1)

    while 1:
        try:
            data_sql = mysql_tengxun.mysql_getdata(sql)
            break

        except:
            time.sleep(1)
            print('get jiroudone data error')


    return data_sql

def creat_dd():

    print("进来看看")
    data_sql=get_order()

    for data in data_sql:

        if data[5]=='添香来黄焖鸡米饭（朝阳店）' or data[5]=='添香来黄焖鸡米饭(朝阳店)':

            order_id=data[9]
            total_price=data[8]
            cost_name=data[19]
            cost_address=data[2].replace(' ','')
            print(cost_address)
            cost_lat=data[13]/1000000
            cost_lng=data[14]/1000000
            platform=data[4]
            order_num=data[6]
            origin_mark_no=platform+str(order_num)

            if data[4]=='美团':
                cost_phone = data[3]
            elif data[4]=='饿了么':
                cost_phone=data[3].replace('[','').replace(']','').replace('"','')

            #达达获取数据
            url = "/api/order/queryDeliverFee"
            body = {
                "shop_no": "63381-4279453",
                "origin_id": order_id,
                "city_code": "010",
                "cargo_price": total_price,
                "is_prepay": "0",
                "receiver_name": cost_name,
                "receiver_address": cost_address,
                "callback": "http://www.tianxlzhuli.com/DD/OrderStatus/",
                "cargo_weight": "2.5",
                "is_use_insurance": "0",
                "receiver_lat": cost_lat,
                "receiver_lng": cost_lng,
                "receiver_phone": cost_phone,
                "origin_mark_no":origin_mark_no
            }

            data_json = do_allps.do_dada(url, body)
            dd_status= jsonpath.jsonpath(data_json, '$..status')[0]

            if dd_status=='success':
                dd_distance= int(jsonpath.jsonpath(data_json, '$..distance')[0])
                dd_fee=jsonpath.jsonpath(data_json, '$..fee')[0]
                deliveryNo=jsonpath.jsonpath(data_json, '$..deliveryNo')[0]


            timestamp = int(time.time())
            jichu_url = "/open/api/external/precreateorder?"
            #顺丰获取数据
            dict_str = {
                "shop_id": "6250508608337",
                "dev_id": "1547215874",
                "user_lng": cost_lng,
                "user_lat": cost_lat,
                "user_address": cost_address,
                "weight": "1000",
                "product_type": "1",
                "is_appoint": "0",
                "push_time": str(timestamp),
                "version": "17",
                "is_person_direct": "0",
                "is_insured": "0",
            }
            data_json = do_allps.do_sf(dict_str, jichu_url)
            sf_status= int(jsonpath.jsonpath(data_json, '$..error_code')[0])
            if sf_status==0:
                sf_distance= jsonpath.jsonpath(data_json, '$..delivery_distance_meter')[0]
                sf_fee=(jsonpath.jsonpath(data_json, '$..estimate_pay_money')[0])/100

            if dd_status=='success' and sf_status==0:

                sql = "insert into ps_price set creat_time='%s',order_id='%s',sf_distance='%s',sf_price='%s',dd_distance='%s',dd_price='%s',platform='%s',order_num='%s'" % (
                    datetime.datetime.now(), order_id, sf_distance,sf_fee, dd_distance,dd_fee,platform,order_num)
                while 1:
                    try:
                        mysql_tengxun.mysql_db(sql)
                        print('insert_one_data')
                        break
                    except:
                        time.sleep(1)
                        print('insert___date__error')
                        continue

                sql = "update order_2 set get_price = '%s' where order_id='%s' " % (1, order_id)

                while 1:
                    try:
                        mysql_tengxun.mysql_db(sql)
                        print('update_one_data')
                        break
                    except:
                        time.sleep(1)
                        print('update_order2_error')
                        continue

                if sf_fee>dd_fee:

                    print("这个单子要发达达"+str(order_id))
                    url = "/api/order/addAfterQuery"

                    body = {
                        "deliveryNo": deliveryNo
                            }

                    data_json = do_allps.do_dada(url, body)
                    dd_status = jsonpath.jsonpath(data_json, '$..status')[0]

                    if dd_status == 'success':

                        sql = "update order_2 set ps_dd = '%s' where order_id='%s' " % (1, order_id)

                        while 1:
                            try:
                                mysql_tengxun.mysql_db(sql)
                                print('update_ps_dd_data')
                                break
                            except:
                                time.sleep(1)
                                print('update_ps_dd_error')
                                continue

                        sql = "update ps_record set dd_fadantime ='%s' where orderid='%s' " % (datetime.datetime.now(), order_id)

                        while 1:
                            try:
                                mysql_tengxun.mysql_db(sql)
                                print('update_dd_fadantime_data')
                                break
                            except:
                                time.sleep(1)
                                print('update_dd_fadantime_data_error')
                                continue
                else:
                    print('达达比顺丰价格高',sf_fee,dd_fee)

    # 声明全局变量
    global t1
    # 创建并初始化线程
    t1 = threading.Timer(3, creat_dd)
    # 启动线程
    t1.start()

def get_dd_status():

    print("实时获取达达的配送情况，并上传")

    now_time = datetime.datetime.now() + datetime.timedelta(hours=-3)

    sql = "SELECT * FROM ps_record WHERE  dd_fadantime is not NULL  and  dd_canceltime is NULL and dd_donetime is NULL and creat_time > '%s'" % (
        now_time)

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

            url = "/api/order/status/query"

            body = {
                "order_id": data[2]
            }

            data_json = do_allps.do_dada(url, body)
            dd_status = jsonpath.jsonpath(data_json, '$..status')[0]

            print(dd_status)
            if dd_status == 'success':

                statusCode = int(jsonpath.jsonpath(data_json, '$..statusCode')[0])

                if statusCode == 2 and data[19]==None:

                    transporterName=jsonpath.jsonpath(data_json, '$..transporterName')[0]
                    transporterPhone=jsonpath.jsonpath(data_json, '$..transporterPhone')[0]

                    sql = "update ps_record set dd_taketime='%s',rider_name='%s',rider_phone='%s' where orderid='%s'" % (datetime.datetime.now(),transporterName,transporterPhone,data[2])

                    while 1:
                        try:
                            mysql_tengxun.mysql_db(sql)
                            break
                        except:
                            time.sleep(1)
                            print('update_sf_taketime_error')
                            continue

                    sql = "update order_2 set peisongy = '%s',peisongy_phone='%s' where order_id='%s'" % (transporterName,transporterPhone, data[2])

                    while 1:
                        try:
                            mysql_tengxun.mysql_db(sql)
                            print('update_peisongy_status')
                            break
                        except:
                            time.sleep(1)
                            print('update_peisongy_error')
                            continue
                if statusCode == 2 or statusCode == 3:

                    transporterLng=jsonpath.jsonpath(data_json, '$..transporterLng')[0]
                    transporterLat=jsonpath.jsonpath(data_json, '$..transporterLat')[0]

                    sql = "update ps_record set dd_status='%s',dd_lng='%s',dd_lat='%s' where orderid='%s'" % (statusCode, transporterLng, transporterLat, data[2])

                    while 1:
                        try:
                            mysql_tengxun.mysql_db(sql)
                            break
                        except:
                            time.sleep(1)
                            print('update_sf_taketime_error')
                            continue

                elif statusCode==4:

                    sql = "update ps_record set dd_status='%s',dd_donetime='%s' where orderid='%s'" % (statusCode, datetime.datetime.now(),data[2])

                    while 1:
                        try:
                            mysql_tengxun.mysql_db(sql)
                            break
                        except:
                            time.sleep(1)
                            print('update_sf_taketime_error')
                            continue

    global t6
    # 去获取应该有的取消时长
    t6 = threading.Timer(3, get_dd_status)
    # 启动线程
    t6.start()

if __name__ == "__main__":



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
        if hours_big > int(datetime.datetime.now().strftime('%H')) > hours_small:
            cancel_long = int(data[1]) * 60

    # 创建并初始化线程,创建订单
    t1 = threading.Timer(3, creat_dd)
    # 启动线程
    t1.start()


    # 去获取应该有的取消时长
    t5 = threading.Timer(30, get_cancel_long)
    # 启动线程
    t5.start()

    # 往服务器传达达的配送情况
    t6 = threading.Timer(3, get_dd_status)
    # 启动线程
    t6.start()