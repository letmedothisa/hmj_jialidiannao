# -*- coding:utf-8 -*-
import datetime
import mysql_tengxun
import time
import jsonpath
import threading
import do_allps

def get_eleorder():

    now_time = datetime.datetime.now() + datetime.timedelta(hours=-3)

    sql = "SELECT * FROM order_2 WHERE platform='%s' and creat_time > '%s' and dingdan_status!='%s' and (shop_id='%s' or shop_id='%s') and peisongy ='%s' and ps_record is NULL and deliverTime='%s'" % (
    '饿了么', now_time, -4, '1848879', '155852887', None,'0')

    while 1:

        try:
            data_sql = mysql_tengxun.mysql_getdata(sql)
            break

        except:
            time.sleep(1)
            print('get jiroudone data error')

    print(data_sql)

    return data_sql

def creat_sf():

    print('进来发单了')

    order_data = get_eleorder()

    print(order_data)

    if order_data:

        for data in order_data:
            print(data[9],data[10])
            if data[4]=='美团':
                order_source = '1'
            elif data[4]=='饿了么':
                order_source = '2'

            orderid = data[9]
            order_num = data[6]
            order_time = data[1]
            costomer = data[19]
            costomer_phone = data[3].replace('[', '').replace(']', '').replace('"', '')
            costomer_address = data[2]
            costomer_lng = data[14]
            costomer_lat = data[13]
            total_price = data[8]
            platform = data[4]

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

            data_json = do_allps.do_sf(dict_str, jichu_url)

            print(data_json)

            error_code = jsonpath.jsonpath(data_json, '$..error_code')[0]

            if error_code == 0:

                sf_order_id=jsonpath.jsonpath(data_json, '$..sf_order_id')[0]

                sql = "update order_2 set ps_record = '%s' where order_id='%s' " % (1, orderid)

                while 1:
                    try:
                        mysql_tengxun.mysql_db(sql)
                        break
                    except:
                        time.sleep(1)
                        print('update_order2_error')
                        break

                sql = "insert into ps_record set creat_time='%s',sf_fadantime='%s',orderid='%s',sf_orderid='%s',platform='%s',order_num='%s',sf_status='%s',dingdan_status='%s'" % (
                    datetime.datetime.now(), datetime.datetime.now(), orderid, sf_order_id, platform, order_num, 1,0)
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
    t1 = threading.Timer(3, creat_sf)
    # 启动线程
    t1.start()


def get_status():

    print('获取订单状态，配送员坐标')

    now_time = datetime.datetime.now() + datetime.timedelta(hours=-3)

    sql = "SELECT * FROM ps_record WHERE platform='%s' and sf_fadantime is not NULL and cancel_time is NULL and sf_donetime is NULL and creat_time>'%s'" % ('饿了么',now_time)

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
            sf_data = do_allps.do_sf(dict_str, jichu_url)

            error_code=jsonpath.jsonpath(sf_data, '$..error_code')[0]

            if error_code==0:

                sf_status = int(jsonpath.jsonpath(sf_data, '$..order_status')[0])

                print(sf_status,data[9],data[10])

                if data[6]==None and (sf_status==10 or sf_status==12):

                    rider_name = jsonpath.jsonpath(sf_data, '$..rider_name')[0]

                    rider_phone = jsonpath.jsonpath(sf_data, '$..rider_phone')[0]

                    sql = "update ps_record set sf_taketime = '%s',sf_status='%s' where orderid='%s'" % (datetime.datetime.now(),sf_status,data[2])

                    while 1:
                        try:
                            mysql_tengxun.mysql_db(sql)
                            print('update_sf_status')
                            break
                        except:
                            time.sleep(1)
                            print('update_order2_error')
                            continue


                    sql = "update order_2 set peisongy = '%s',peisongy_phone='%s' where order_id='%s'" % (rider_name,rider_phone, data[2])

                    while 1:
                        try:
                            mysql_tengxun.mysql_db(sql)
                            print('update_peisongy_status')
                            break
                        except:
                            time.sleep(1)
                            print('update_peisongy_error')
                            continue


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

                    error_code = jsonpath.jsonpath(sf_data, '$..error_code')[0]

                    if error_code == 0:

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
                                print('update_sf_lng_error')
                                continue

                if sf_status==17:

                    sql = "update ps_record set sf_donetime='%s' where orderid='%s' " % (datetime.datetime.now(),data[2])

                    while 1:
                        try:
                            mysql_tengxun.mysql_db(sql)
                            print('update_sf_lng')
                            break
                        except:
                            time.sleep(1)
                            print('update_sf_lng_error')
                            continue

    # 去时刻查看棋手位置和配送状态，并回传
    global t3

    t3 = threading.Timer(10, get_status)
    # 启动线程
    t3.start()

if __name__ == "__main__":
    # 创建并初始化线程,创建订单
    t1 = threading.Timer(3, creat_sf)
    # 启动线程
    t1.start()


    # 去时刻查看棋手位置和配送状态，并回传
    t3 = threading.Timer(10, get_status)
    # 启动线程
    t3.start()
