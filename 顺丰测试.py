# -*- coding:utf-8 -*-
import time
import base64
import hashlib
import requests
import json


timestamp=int(time.time())

jichu_url="/open/api/external/getshopaccountbalance?"
dict_str={"shop_id":"6250508608337","dev_id":"1547215874","push_time":str(timestamp)}
push_str=(str(dict_str)+'&1547215874&98fd298d895379335a8d85a7ed5917c5').replace("'",'"')


#计算base64
str_md5 = hashlib.md5(push_str.encode(encoding='utf-8')).hexdigest()
bytes_url = str_md5.encode("utf-8")
str_url = base64.b64encode(bytes_url)  # 被编码的参数必须是二进制数据
str_url=str_url.decode('UTF-8')
url = "https://openic.sf-express.com"+jichu_url+"sign="+str(str_url)


payload = json.dumps(dict_str)
payload.replace(' ','').replace("'",'"')

headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)

#---------------------------------------22222222222222

timestamp=int(time.time())

jichu_url="/open/api/external/getorderstatus?"
dict_str={"order_id":"3452222134544436225","dev_id":"1547215874","order_type":"1","push_time":str(timestamp)}
push_str=(str(dict_str)+'&1547215874&98fd298d895379335a8d85a7ed5917c5').replace("'",'"')

#计算base64
str_md5 = hashlib.md5(push_str.encode(encoding='utf-8')).hexdigest()
bytes_url = str_md5.encode("utf-8")
str_url = base64.b64encode(bytes_url)  # 被编码的参数必须是二进制数据
str_url=str_url.decode('UTF-8')
url = "https://openic.sf-express.com"+jichu_url+"sign="+str(str_url)


payload = json.dumps(dict_str)
payload.replace(' ','').replace("'",'"')

headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)