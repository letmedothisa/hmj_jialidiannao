# -*- coding:utf-8 -*-
import hashlib
import mysql_dbggg
import time
import requests
import json
import jsonpath




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

def get_dingdan(orderid):
  #获取sign
  timestamp = int(time.time())
  order_id=str(orderid)
  biz={'biz':{"orderId":order_id}}
  basic_zd = {'appAuthToken': '5d579664aaa45e487c6dab03dbaaf595ed54468034c05ffe41a554781c8c2a479923dee7c442c471ab34b21e162a6956','timestamp': timestamp, 'charset': 'utf-8', 'developerId': 100789, 'version': 2}
  basic_payload=basic_zd
  basic_payload_2=basic_zd
  basic_zd.update(biz)

  sign=get_sign(basic_zd)


  #获取配送费
  sign={'sign':sign}
  fix_zd=json.dumps({"orderId":order_id})
  biz={'biz':fix_zd}


  basic_payload.update(biz)
  basic_payload.update(sign)

  url = "https://api-open-cater.meituan.com/waimai/order/queryById"

  headers = {
  'Content-Type': 'application/x-www-form-urlencoded'
  }

  response = requests.request("POST", url, headers=headers, data=basic_payload)

  return response.text


if __name__=='__main__':

  orderid='18488790223330567'

  shangpin=get_dingdan(orderid)

  shangpin=json.loads(shangpin)

  print(shangpin)

  arrivel_time = jsonpath.jsonpath(shangpin, '$..deliveryTime')

  print(arrivel_time)

  caution = jsonpath.jsonpath(shangpin, '$..caution')

  print(caution)

  ddd=shangpin['data']['detail']

  ddd=json.loads(ddd)

  li=[]

  for i in range(len(ddd)):
    li_1=[]
    res1 = jsonpath.jsonpath(ddd[i], '$..food_name')
    li_1.append(res1)
    res1 = jsonpath.jsonpath(ddd[i], '$..quantity')
    li_1.append(res1)
    res1 = jsonpath.jsonpath(ddd[i], '$..food_property')
    li_1.append(res1)
    res1 = jsonpath.jsonpath(ddd[i], '$..spec')
    li_1.append(res1)
    li.append(li_1)

  print(li)