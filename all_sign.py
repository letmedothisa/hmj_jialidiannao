# -*- coding:utf-8 -*-
import datetime
import os
import time
import all_sign_lunkuo
import mysql_tengxun

def get_lunkuo(file_path, li_range, first_standard, lunkuo_small, lunkuo_big, bili_small, bili_big, zaotai_num):

    files = os.listdir(file_path)
    if len(files) > 2:
        file_pic = file_path + files[-2]
        try:
            yaji_outline1 = all_sign_lunkuo.main(li_range, file_pic, first_standard, lunkuo_small, lunkuo_big)
            for i in range(len(yaji_outline1)):
                if bili_big > yaji_outline1[i][0] / (
                        2 * (yaji_outline1[i][2] - yaji_outline1[i][1] + yaji_outline1[i][4] - yaji_outline1[i][
                    3])) > bili_small:
                    sql = "insert into zaotai_sign set creat_time='%s',zaotai_num='%s',sign_x='%s',sign_y='%s'" % (
                    datetime.datetime.now(), zaotai_num, yaji_outline1[i][5], yaji_outline1[i][6])
                    while 1:
                        try:
                            mysql_tengxun.mysql_db(sql)
                            print('insert_one_data')
                            break
                        except:
                            time.sleep(1)
                            print('insert___date__error')
                            break
        except:
            time.sleep(1)
            print('get lunkuo error')

# ----------------------------获取左边的灶台---------------------------------
while 1:

    #从txt文件里读取内容
    with open('config.txt', 'r') as f:
        a = f.readlines()
        for i in range(len(a)):
            b = a[i].split(' ')
            if b[0] == 'all_sign':
                file_path_pre=b[1].split('=')[1]
                li_range=[]
                li_range_1=b[2].split('=')[1].split(',')
                for j in range(len(li_range_1)):
                    li_range.append(int(li_range_1[j]))
                zaotai_num=int(b[3].split('=')[1])
                judge_standard=int(b[4].split('=')[1])
                lunkuo_small=int(b[5].split('=')[1])
                lunkuo_big=int(b[6].split('=')[1])
                bili_small=float(b[7].split('=')[1])
                bili_big=float(b[8].replace('\n','').split('=')[1])
                file_path = file_path_pre + datetime.datetime.now().strftime('%Y-%m-%d') + '_pic/'
                get_lunkuo(file_path, li_range, judge_standard, lunkuo_small, lunkuo_big, bili_small, bili_big, zaotai_num)


    time.sleep(60)