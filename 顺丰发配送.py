# -*- coding:utf-8 -*-
import time
import base64
import hashlib
import requests
import json
import jsonpath


def get_mt_sign(data):

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

    sign = hashlib.sha1(string_sign.encode('utf-8')).hexdigest()
    return sign


def deal_mt(orderid,url_1,fix_biz):

    # 获取sign
    timestamp = int(time.time())
    order_id = str(orderid)
    biz = {'biz': fix_biz}
    basic_zd = {
        'appAuthToken': '5d579664aaa45e487c6dab03dbaaf595ed54468034c05ffe41a554781c8c2a479923dee7c442c471ab34b21e162a6956',
        'timestamp': timestamp, 'charset': 'utf-8', 'developerId': 100789, 'version': 2}
    basic_payload = basic_zd
    basic_payload_2 = basic_zd
    basic_zd.update(biz)

    sign = get_mt_sign(basic_zd)

    # 获取配送费
    sign = {'sign': sign}
    biz = {'biz': fix_biz}

    basic_payload.update(biz)
    basic_payload.update(sign)

    url = url_1

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data=basic_payload)

    return response.text

def creat_dd():

	timestamp=int(time.time())

	jichu_url="/api/order/addOrder"

	dict_str = {
		"shop_no": "63381-4279453",
		"origin_id":str(orderid),
		"city_code": "1547215874",
		"cargo_price": str(order_source),
		"is_prepay":str(order_num),
		"receiver_name": "1",
		"receiver_address":"2",
		"receiver_lat": str(order_time),
		"receiver_lng": "0",
		"callback": "0",
		"cargo_weight":str(timestamp),
	}

def dd_get_chengshicode():

	timestamp=int(time.time())
	jichu_url="/api/order/addOrder"
	app_secret="acdc9efb79db1fad06a59dea5f3eb5e3"
	dict_str =  {
    "app_key": "dadae480b0594b5b90c",
    "body": "",
    "format": "json",
    "source_id": "63381-4279453",
    "timestamp":timestamp,
    "v": "1.0",
    "app_secret": "acdc9efb79db1fad06a59dea5f3eb5e3"
 }

	list_dict=sorted(dict_str.keys())
	print(list_dict)
	str_list=app_secret
	for item in list_dict:
		if item=='app_secret':
			continue
		else:
			str_list+=str(dict_str[item])

	str_list+=app_secret




def creat_sf(orderid,order_source,order_num,order_time,costomer,costomer_phone,costomer_address,costomer_lng,costomer_lat,total_price):

	timestamp=int(time.time())

	jichu_url="/open/api/external/createorder?"

	dict_str = {
		"shop_id": "6250508608337",
		"shop_order_id":str(orderid),
		"dev_id": "1547215874",
		"order_source": str(order_source),
		"order_sequence":str(order_num),
		"pay_type": "1",
		"lbs_type":"2",
		"order_time": str(order_time),
		"is_appoint": "0",
		"is_person_direct": "0",
		"push_time":str(timestamp),
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

	push_str=(str(dict_str)+'&1547215874&98fd298d895379335a8d85a7ed5917c5').replace("'",'"')


	#计算base64
	str_md5 = hashlib.md5(push_str.encode(encoding='utf-8')).hexdigest()
	bytes_url = str_md5.encode("utf-8")
	str_url = base64.b64encode(bytes_url)  # 被编码的参数必须是二进制数据
	str_url=str_url.decode('UTF-8')

	url = "https://openic.sf-express.com"+jichu_url+"sign="+str(str_url)

	payload = json.dumps(dict_str,ensure_ascii=False)
	payload.replace(' ','').replace("'",'"')
	print(payload)
	headers = {
	  'Content-Type': 'application/json'
	}

	response = requests.request("POST", url, headers=headers, data=payload)

	print(response.text)

# -----------------------------------取消订单-----------------------------------------------

def cancel_sf(orderid):

	timestamp = int(time.time())

	dict_str = {
		"order_id": str(orderid),
		"order_type": "2",
		"dev_id": "1547215874",
		"push_time": str(timestamp)
	}
	push_str = (str(dict_str) + '&1547215874&98fd298d895379335a8d85a7ed5917c5').replace("'", '"')

	# 计算base64
	str_md5 = hashlib.md5(push_str.encode(encoding='utf-8')).hexdigest()
	bytes_url = str_md5.encode("utf-8")
	str_url = base64.b64encode(bytes_url)  # 被编码的参数必须是二进制数据
	str_url = str_url.decode('UTF-8')

	url = "https://openic.sf-express.com/open/api/external/createorder?sign=" + str(str_url)

	payload = json.dumps(dict_str)
	payload.replace("'", '"')

	headers = {
		'Content-Type': 'application/json'
	}

	response = requests.request("POST", url, headers=headers, data=payload)

	print(response.text)


def cancel_mt_reason(orderid):

	# timestamp = int(time.time())
	url = 'https://api-open-cater.meituan.com/waimai/order/queryZbCancelDeliveryReason'

	biz = {"orderId": orderid}
	biz = json.dumps(biz)

	get_data = deal_mt(orderid, url, biz)

	data_json = json.loads(get_data)

	reason = jsonpath.jsonpath(data_json, '$..code')


def cancal_mt(orderid,reasonCode,reasonContent):

	# timestamp = int(time.time())
	url = 'https://api-open-cater.meituan.com/waimai/order/cancelZbLogisticsByWmOrderId'

	biz = {
		"detailContent": reasonContent,
		"orderId": orderid,
		"reasonCode": reasonCode
	}
	biz = json.dumps(biz)

	get_data = deal_mt(orderid, url, biz)

	data_json = json.loads(get_data)
	arrivel_time = jsonpath.jsonpath(data_json, '$..code')

