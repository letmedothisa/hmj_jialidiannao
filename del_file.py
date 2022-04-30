# -*- coding:utf-8 -*-
import os
import datetime
import time


def del_file(file_path, day, hours, minutes):
    # 先把这个路径里的文件都拿出来，适合只有一级目录的情况
    dir_list = os.listdir(file_path)

    # 如果有文件，就挨个获取文件的最后修改时间，如果
    if dir_list:

        dir_list = sorted(dir_list, key=lambda x: os.path.getmtime(os.path.join(file_path, x)),reverse=True)

        for i in range(1,len(dir_list)):
            file_pic = file_path + dir_list[i]

            try:
                get_mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(file_pic)))

                get_mtime = datetime.datetime.strptime(get_mtime, "%Y-%m-%d %H:%M:%S")

                now_time = datetime.datetime.now() + datetime.timedelta(days=-day, hours=-hours, minutes=-minutes)

                if get_mtime < now_time:
                    os.remove(file_pic)
            except:
                print('get_mtime_error' + file_pic)
                with open ('del_file_error.txt','a') as f:
                    f.write('get_mtime_error' + file_pic+'\n')

    if os.path.exists('del_file_error.txt'):
        if os.path.getsize('del_file_error.txt') > 1000000:
            os.remove('del_file_error.txt')

if __name__ == '__main__':
    del_file()