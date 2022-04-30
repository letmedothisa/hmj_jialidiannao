# -*- coding:utf-8 -*-
import time
import os
import mysql_tengxun
import guo_lunkuo_yx
import datetime

li_range = [431, 148, 260, 170]

dowhat = 'chucan'

with open('config.txt', 'r') as f:
    a = f.readlines()
    for i in range(len(a)):
        b = a[i].split(' ')
        if b[0] == dowhat:
            picture_path = b[3].replace("\n", "").replace("\r", "").split('=')[1]

lunkuo_big = 400
lunkuo_small = 35




def get_xy():

    data_item = []

    get_time=datetime.datetime.now()+datetime.timedelta(hours=-1)

    sql = "SELECT * FROM guo_center WHERE  guo_center.creat_time>'%s'" % (get_time)
    while 1:
        try:
            data_item = mysql_tengxun.mysql_getdata(sql)
            break

        except:
            time.sleep(1)
            print('get gaoya_position data error')
            break

    if data_item:

        center_x=data_item[-1][2]
        center_y=data_item[-1][3]

    else:
        center_x=574
        center_y=327

    return center_x,center_y



while 1:

    file_path = picture_path + datetime.datetime.now().strftime('%Y-%m-%d') + '_pic/'
    if not os.path.exists(file_path):
        os.makedirs(file_path)

    first_standard = 200

    file = os.listdir(file_path)

    file_pic = file_path + file[-1]

    outline = []
    find_or = False

    while first_standard > 130:

        try:
            outline = guo_lunkuo_yx.main(li_range, file_pic, first_standard, lunkuo_small, lunkuo_big)
        except:
            print('get_lunkuo_error')

        #去服务器拿之前存储的center_x和center_y

        center_x_sql,center_y_sql=get_xy()

        if outline:
            
            li_find=[]
            for i in range(len(outline)):

                min_x = outline[i][1]
                max_x = outline[i][2]
                min_y = outline[i][3]
                max_y = outline[i][4]
                center_x = outline[i][5]
                center_y = outline[i][6]
                x_long = outline[i][7]
                y_long = outline[i][8]

                li_find.append(abs(center_x_sql-center_x)+abs(center_y_sql-center_y))

            position=li_find.index(min(li_find))

            min_x = outline[position][1]
            max_x = outline[position][2]
            min_y = outline[position][3]
            max_y = outline[position][4]
            center_x = outline[position][5]
            center_y = outline[position][6]
            x_long = outline[position][7]
            y_long = outline[position][8]

            for j in range(300):
                yuanxin_x = center_x + (y_long / x_long) * j

                yuanxin_y = center_y + j

                print(yuanxin_x - min_x)
                print(yuanxin_y - min_y)

                print((yuanxin_x - min_x) * (yuanxin_x - min_x) + (yuanxin_y - max_y) * (yuanxin_y - max_y) - 18906)

                if abs((yuanxin_x - min_x) * (yuanxin_x - min_x) + (yuanxin_y - max_y) * (
                        yuanxin_y - max_y) - 18906) < 200:

                    yuanxin_x = int(yuanxin_x)
                    yuanxin_y = int(yuanxin_y)
                    print(yuanxin_x, yuanxin_y)
                    sql = "insert into guo_center set creat_time='%s',center_x='%s',center_y='%s',biaoji_x='%s',biaoji_y='%s'" % (
                        datetime.datetime.now(), yuanxin_x, yuanxin_y, min_x, max_y)
                    while 1:
                        try:
                            mysql_tengxun.mysql_db(sql)
                            print('insert_one_data')
                            find_or = True
                            print('找到了一个符合要求的，标准是：' + str(first_standard))
                            break
                        except:
                            time.sleep(1)
                            print('insert___date__error')
                            break
                    break

        if find_or == True:
            break
        else:
            first_standard -= 20

    time.sleep(120)