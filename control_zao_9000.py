# -*- coding:utf-8 -*-
import threading
import time
import socket
from tkinter import messagebox
import mysql_tengxun
import datetime


def get_zaoyan():
    global li_dcf
    global li_dianh
    global li_kaig

    data_sql = 0

    sql = "select * from zao_setting"

    while 1:
        try:
            data_sql = mysql_tengxun.mysql_getdata(sql)
            break

        except:
            time.sleep(1)
            print('get_zao_setting_error')
            break

    if data_sql == 0 or not data_sql:
        return 0

    else:

        li_dcf = []
        li_dianh = []
        li_kaig = []

        for i in range(len(data_sql)):
            # 所有配置搞好
            li_dcf_1 = []
            li_dcf_1.append(data_sql[i][3])
            li_dcf_1.append(data_sql[i][4])
            li_dcf.append(li_dcf_1)
            li_dianh_1 = []
            li_dianh_1.append(data_sql[i][5])
            li_dianh_1.append(data_sql[i][6])
            li_dianh.append(li_dianh_1)
            li_kaig_1 = []
            li_kaig_1.append(data_sql[i][7])
            li_kaig_1.append(data_sql[i][8])
            li_kaig.append(li_kaig_1)

        return data_sql

    global t5
    # 启动服务器，接收指令，并侦测状态
    t5 = threading.Timer(10, get_zaoyan)
    t5.start()


def deal_sqldata():
    global li_sqldata

    if li_sqldata:
        sql = li_sqldata[0]
        while 1:
            try:
                mysql_tengxun.mysql_db(sql)
                print('成功上传一条数据')
                del li_sqldata[0]
                break
            except:
                time.sleep(0.3)
                print('deal_sqldata_error')
                break

    global t4
    # 启动服务器，接收指令，并侦测状态
    t4 = threading.Timer(1, deal_sqldata)
    t4.start()


def close_dianhuo():
    global li_cunchu

    print(li_cunchu)

    for i in range(len(data_zao)):

        if li_cunchu[i][2] != 0:

            # 点火6秒钟
            if (datetime.datetime.now() - li_cunchu[i][2]).seconds > 6:

                com_dianh = li_dianh[i][0]
                pos_dianh = li_dianh[i][1]
                content = 'close' + ',' + str(pos_dianh)

                recive_data = socket_client(com_dianh, content)
                if recive_data == 'ok':
                    print('点火器到点关火成功')
                    li_cunchu[i][2] = 0

        if li_cunchu[i][1] != 0:

            if li_duration:
                duration = int(li_duration[i][3]) * 60
            else:
                duration = 1080

            # 点火6秒钟
            if (datetime.datetime.now() - li_cunchu[i][1]).seconds > duration:

                com_dcf = li_dcf[i][0]
                pos_dcf = li_dcf[i][1]

                content = 'close' + ',' + str(pos_dcf)
                recive_data = socket_client(com_dcf, content)

                if recive_data == 'ok':
                    print('灶台到点关火成功')

                    # 数据上传到服务器
                    yaji_long = round((datetime.datetime.now() - li_cunchu[i][1]).seconds / 60, 2)
                    sql = "update shangqi_2 set yaji_long = '%s',guanhuo_time ='%s' where yaji_time = '%s'" % (
                        yaji_long, datetime.datetime.now(), li_cunchu[i][1])
                    li_sqldata.append(sql)

                    sql = "update zao_record set cook_long = '%s',guanhuo_time ='%s' where dianhuo_time = '%s'" % (
                        yaji_long, datetime.datetime.now(), li_cunchu[i][1])
                    li_sqldata.append(sql)

                    li_cunchu[i][1] = 0

    global t3
    # 启动点火线程
    t3 = threading.Timer(0.5, close_dianhuo)
    t3.start()


def dianhuo():
    global li_do
    global li_cunchu

    if li_do:

        zaoyan = int(li_do[0])

        sql = "select * from zao_setting where zaoyan='%s'" % (zaoyan)

        while 1:
            try:
                data_sql = mysql_tengxun.mysql_getdata(sql)
                break

            except:
                time.sleep(1)
                print('get_zao_setting_error')
                break

        if data_sql:

            # 这里是电池阀操作
            com_dcf = data_sql[0][3]

            if com_dcf != 100 and com_dcf != None:
                pos_dcf = data_sql[0][4]

                if li_cunchu[zaoyan][1] == 0:
                    operate = 'open'
                else:
                    operate = 'close'

                content = operate + ',' + str(pos_dcf)
                data_dcf = socket_client(com_dcf, content)

                if data_dcf == 'ok':

                    if operate == 'open':

                        print('灶台开火成功')
                        dianhuo_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        dianhuo_time = datetime.datetime.strptime(dianhuo_time, '%Y-%m-%d %H:%M:%S')

                        li_cunchu[zaoyan][1] = dianhuo_time

                        sql = "insert into zao_record set zaoyan = '%s',dianhuo_time = '%s'" % (
                            zaoyan, dianhuo_time)

                        li_sqldata.append(sql)

                        # 这里转换一下灶台和灶眼
                        if zaoyan > 5:
                            zaotai = 1
                            zaoyan_cg = zaoyan - 6
                        else:
                            zaotai = 0
                            zaoyan_cg = zaoyan

                        # 上传到两个服务器
                        sql = "insert into shangqi_2 set zaotai = '%s',zaoyan = '%s',creat_time = '%s',yaji_time = '%s'" % (
                            zaotai, zaoyan_cg, dianhuo_time, dianhuo_time)

                        li_sqldata.append(sql)

                        del li_do[0]

                    elif operate == 'close':

                        print('灶台关火成功')

                        # 数据上传到服务器
                        yaji_long = round((datetime.datetime.now() - li_cunchu[zaoyan][1]).seconds / 60, 2)
                        sql = "update shangqi_2 set yaji_long = '%s',guanhuo_time ='%s' where yaji_time = '%s'" % (
                            yaji_long, datetime.datetime.now(), li_cunchu[zaoyan][1])
                        li_sqldata.append(sql)

                        sql = "update zao_record set cook_long = '%s',guanhuo_time ='%s' where dianhuo_time = '%s'" % (
                            yaji_long, datetime.datetime.now(), li_cunchu[zaoyan][1])
                        li_sqldata.append(sql)

                        li_cunchu[zaoyan][1] = 0

                        del li_do[0]

            else:
                del li_do[0]

            # 这里是点火器操作
            com_dcf = data_sql[0][5]

            if com_dcf != 100 and com_dcf != None:

                if li_cunchu[zaoyan][1] == 0:

                    pos_dcf = data_sql[0][6]
                    operate = 'open'
                    content = operate + ',' + str(pos_dcf)
                    data_dcf = socket_client(com_dcf, content)

                    if data_dcf == 'ok':
                        dianhuo_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        dianhuo_time = datetime.datetime.strptime(dianhuo_time, '%Y-%m-%d %H:%M:%S')

                        li_cunchu[zaoyan][2] = dianhuo_time
                        print('点火器点火成功')

    global t2
    # 启动点火线程
    t2 = threading.Timer(0.5, dianhuo)
    t2.start()


def get_timelong():
    global li_duration

    sql = "SELECT * FROM zaoyan_timelong"

    li_duration = mysql_tengxun.mysql_getdata(sql)

    global t6
    # 启动服务器，接收指令，并侦测状态
    t6 = threading.Timer(10, get_timelong)
    t6.start()


def socket_server():
    global li_do
    # 创建 socket 对象
    s = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM)
    # 获取本地主机名
    host = socket.gethostname()
    port = control_port
    # 绑定端口
    s.bind((host, port))
    # 设置最大连接数，超过后排队
    s.listen(5)
    while True:
        # 建立客户端连接
        conn, addr = s.accept()
        recive_data = conn.recv(1024)
        recive_data = recive_data.decode('utf-8')
        li_do.append(recive_data)
        print('9000----接到命令', recive_data)
        conn.send('ok'.encode('utf-8'))
        conn.close()


def socket_client(com, content):
    content = str(content)
    # 创建 socket 对象
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 获取本地主机名
    host = socket.gethostname()
    # 设置端口号
    port = 8000 + com
    # 连接服务，指定主机和端口
    s.connect((host, port))
    # 接收小于 1024 字节的数据
    s.send(content.encode('utf-8'))
    print('9000----发出命令', content)
    recive_data = s.recv(1024)
    recive_data = recive_data.decode('utf-8')
    s.close()
    return recive_data


if __name__ == '__main__':

    li_cunchu = []
    li_dcf = []
    li_dianh = []
    li_kaig = []
    li_duration = []
    li_do = []
    li_sqldata = []

    # a = sys.executable
    # b = a.split('\\')
    # get_com = False
    #
    # for i in range(len(b)):
    #     if 'exe' in b[i]:
    #         control_port = int(b[i].split('.')[0].split('_')[2])
    #         get_com = True

    # 测试专用
    control_port = 9000
    get_com = True

    if get_com == True:

        data_zao = get_zaoyan()

        if data_zao == 0:
            messagebox.showinfo('提示', '没拿到灶台相关信息，请关注！')
        else:
            for i in range(len(data_zao)):
                li_cunchu.append([i, 0, 0])

        # 启动主函数
        t1 = threading.Thread(target=socket_server)
        t1.start()

        # 启动点火线程
        t2 = threading.Timer(0.5, dianhuo)
        t2.start()

        # 启动服务器，接收指令，并侦测状态
        t3 = threading.Timer(0.5, close_dianhuo)
        t3.start()

        # 启动服务器，接收指令，并侦测状态
        t4 = threading.Timer(1, deal_sqldata)
        t4.start()

        # 启动服务器，接收指令，并侦测状态
        t5 = threading.Timer(10, get_zaoyan)
        t5.start()

        # 启动服务器，接收指令，并侦测状态
        t6 = threading.Timer(10, get_timelong)
        t6.start()

    else:

        messagebox.showinfo('提示', '没有找到dowhat信息，请注意！')