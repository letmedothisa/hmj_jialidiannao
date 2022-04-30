import datetime

import getall_basedata

def get_zhengfan_data():

    long=round((datetime.datetime.now()-datetime.datetime.strptime('00：00：00 00：00：00','%Y-%m-%d %H:%M:%S')).seconds/3600,2)
    zhengfan_data=getall_basedata.get_data(long,'zhengfan','creat_time')

    if zhengfan_data:
