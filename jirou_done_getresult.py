# -*- coding:utf-8 -*-
import datetime
import os
import sys
import all_getresult
import del_file
import time
import get_hsv
import mysql_tengxun

cutpic_time = datetime.datetime.now()
del_cutpictime = datetime.datetime.now()
del_pictime=datetime.datetime.now()
keep_on = datetime.datetime.now()
li_lunkuo = []
li_lunkuo_heng = []
# 获取exe信息
a = sys.executable
b = a.split('\\')
for i in range(len(b)):
    if 'exe' in b[i]:
        dowhat = b[i].split('.')[0]

dowhat = 'jiroudone_getresult'
# 获取所有的config信息

# 去拿RPG的标准值了
with open('config.txt', 'r') as f:
    a = f.readlines()
    for i in range(len(a)):
        b = a[i].split(' ')
        if dowhat.split('_')[0] + '_' + 'hsv' in b[0]:
            r1 = int(b[1])
            r2 = int(b[2])
            r3 = int(b[3])
            r4 = int(b[4])
            r5 = int(b[5])
            r6 = int(b[6].replace('\n', ''))

        if dowhat.split('_')[0] + '_' + 'guo' in b[0]:
            x_guo = int(b[1])
            y_guo = int(b[2])
            x_long_guo = int(b[3])
            y_long_guo = int(b[4])
            guo_times = int(b[5].replace('\n', ''))

        if dowhat.split('_')[0] + '_' + 'pen' in b[0]:
            x_pen = int(b[1])
            y_pen = int(b[2])
            x_long_pen = int(b[3])
            y_long_pen = int(b[4])
            pen_times = int(b[5].replace('\n', ''))

config = all_getresult.get_config('chucan_getresult')
updata_time=datetime.datetime.now()

while 1:
    # 先把要处理的文件夹搞定
    file_path = config[0] + datetime.datetime.now().strftime('%Y-%m-%d') + '_pic/'

    if not os.path.exists(file_path):
        os.makedirs(file_path)

    if (datetime.datetime.now() - del_pictime).seconds > int(config[1]) * 60:
        # 把清除图片的时间赋值回来
        del_pictime = datetime.datetime.now()
        del_file.del_file(file_path, 0, 0, int(config[1]))

    if (datetime.datetime.now() - del_cutpictime).days >= config[3]:
        print('进来删除图片啦')
        del_cutpictime = datetime.datetime.now()
        del_file.del_file(config[2], config[3], 0, 0)

    dir_list = os.listdir(file_path)
    geterror = False
    if dir_list:
        if len(dir_list) > 2:
            try:
                dir_list = sorted(dir_list, key=lambda x: os.path.getmtime(os.path.join(file_path, x)),
                                  reverse=True)
            except:
                geterror = True

            if geterror == False:
                file_path_pic = file_path + dir_list[1]
        # 先去看锅的位置的情况：
        guo_num = 0
        total_guo=0
        for j in range(guo_times):
            x_guo_linshi = x_guo + x_long_guo * j
            h, s, v, place = get_hsv.gethsv(file_path_pic, x_guo_linshi, y_guo, x_long_guo, y_long_guo)

            guo_jirou_num = 0
            for i in range(len(h)):
                if (r1 < h[i] < r2 and r3 < s[i] < r4 and r5 < v[i] < r6):
                    guo_jirou_num += 1
            if guo_jirou_num > 2000:
                print('找到一个锅有肉的情况！')
                guo_num += 1
                total_guo+=guo_jirou_num

        # 再先去看看盆的情况：
        pen_num = 0
        total_pen=0
        for j in range(pen_times):
            x_pen_linshi = x_pen + x_long_pen * j
            h, s, v, place = get_hsv.gethsv(file_path_pic, x_pen_linshi, y_pen, x_long_pen, y_long_pen)
            pen_jirou_num = 0
            for i in range(len(h)):
                if (r1 < h[i] < r2 and r3 < s[i] < r4 and r5 < v[i] < r6):
                    pen_jirou_num += 1

            if pen_jirou_num > 2000:
                print('找到一个盆有肉的情况！')
                pen_num += 1
                total_pen+=pen_jirou_num

        print(guo_num,pen_num,total_guo,total_pen)
        with open('guo_pen.txt', 'a') as f:
            f.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '锅有多少----%d,,,盆有多少-----%d' % (
            guo_num, pen_num) + '\n')

        if (datetime.datetime.now()-updata_time).seconds>10:

            sql = "insert into jiroudone set creat_time = '%s',guo_num= '%s',pen_num= '%s',guo_total= '%s',pen_total= '%s'" % (datetime.datetime.now(),guo_num,pen_num,total_guo,total_pen)

            while 1:
                try:
                    mysql_tengxun.mysql_db(sql)
                    updata_time=datetime.datetime.now()
                    break
                except:
                    with open('eroor_jiroudone_getresult.txt', 'a') as f:
                        f.write(
                            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '_insert_jiroudone_error_' + '\n')
                    time.sleep(1)
                    continue

    time.sleep(5)
    print(datetime.datetime.now())