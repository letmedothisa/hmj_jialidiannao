# -*- coding:utf-8 -*-
import datetime
import threading
import serial
import time
import binascii
import socket
from tkinter import messagebox
import mysql_tengxun


def deal_sqldata():
    global li_sqldata

    if li_sqldata:
        sql = li_sqldata[0]
        while 1:
            try:
                mysql_tengxun.mysql_db(sql)
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


def get_kaig():
    global li_kaig
    global li_zaoy
    global li_zaotai
    global do_kaig
    global li_cunchu

    data_sql = 0

    sql = "select * from kaig_setting where com_num='%s' and status is not NULL" % (com)

    while 1:
        try:
            data_sql = mysql_tengxun.mysql_getdata(sql)
            break

        except:
            time.sleep(1)
            print('get_kaig_data_error')
            break

    if data_sql == 0:
        return 0

    elif not data_sql:

        do_kaig = False

    else:

        do_kaig = True
        li_kaig = []
        li_zaotai = []
        li_zaoy = []
        li_cunchu = []
        for i in range(6):
            if i == int(data_sql[i][2]):
                li_kaig.append(data_sql[i][3])
                li_zaotai.append(data_sql[i][4])
                li_zaoy.append(data_sql[i][5])
                li_cunchu.append(0)

    global t3
    # 启动服务器，接收指令，并侦测状态
    t3 = threading.Timer(10, get_kaig)
    t3.start()


def operate_dcf():
    global li_do

    print(li_do)

    operate = li_do[0].replace("'", '').split(',')[0]

    position = int(li_do[0].replace("'", '').split(',')[1])

    print(operate, position)

    if operate == 'open':

        do_operate = li_open[position]
    else:
        do_operate = li_close[position]

    if ser.isOpen():

        ser.flushInput()

        result = ser.write(bytes.fromhex(do_operate))

        if result != 0:

            times = 0

            while 1:

                len_return_data = ser.inWaiting()
                time.sleep(0.01)
                times += 1

                if len_return_data != 0:

                    if len(li_do) > 0:
                        del li_do[0]

                    break

                if times == 100:
                    print('操作电磁阀失败')


def read_dcf():
    global li_sqldata

    if ser.isOpen():

        ser.flushInput()

        result = ser.write(bytes.fromhex(read_do_sta))

        if result != 0:

            times = 0
            while 1:

                len_return_data = ser.inWaiting()
                time.sleep(0.01)
                times += 1

                if len_return_data != 0:

                    try:
                        # 处理拿到的数据
                        read_data = ser.read(len_return_data)
                        get_result = str(binascii.b2a_hex(read_data))[8:-5]
                        b = list(bin(int(get_result, 16))[2:].zfill(6))
                        b = b[::-1]

                        if len(b) == 6:
                            sql = "update dcf_status set position_0 = '%s',position_1 = '%s',position_2 = '%s',position_3 = '%s',position_4 = '%s',position_5 = '%s',creat_time ='%s' where com='%s'" % (
                                int(b[0]), int(b[1]), int(b[2]), int(b[3]), int(b[4]), int(b[5]),
                                datetime.datetime.now(),
                                com)
                            li_sqldata.append(sql)

                        break
                    except:
                        print('读取do错误，请关注')
                        break

                if times > 100:
                    print('1秒之内没有拿到数据')
                    break


def read_kg(read_sta):
    global li_cunchu

    if ser.isOpen():

        ser.flushInput()

        result = ser.write(bytes.fromhex(read_sta))

        if result != 0:

            times = 0
            while 1:

                len_return_data = ser.inWaiting()
                time.sleep(0.01)
                times += 1

                if len_return_data != 0:

                    try:
                        # 处理拿到的数据
                        read_data = ser.read(len_return_data)
                        get_result = str(binascii.b2a_hex(read_data))[8:-5]
                        b = list(bin(int(get_result, 16))[2:].zfill(6))
                        b = b[::-1]

                        # print(b,'-------',datetime.datetime.now())
                        # 如果数据符合要求
                        if len(b) == 6:

                            for i in range(len(b)):

                                # 如果拿到的开关状态和存储的默认开关状态不符合
                                if int(b[i]) != int(li_kaig[i]):

                                    if li_cunchu[i] == 0:
                                        # 需要传输port 和content,content里面有com口和zaoyan信息

                                        content = str(li_zaoy[i])
                                        data_recive = socket_client(content)
                                        if data_recive == 'ok':
                                            li_cunchu[i] = datetime.datetime.now()

                                    elif (datetime.datetime.now() - li_cunchu[i]).seconds > 3:
                                        li_cunchu[i] = 0

                            break
                        else:

                            break
                    except:
                        print('解析拿到数据错误')
                if times > 100:
                    break
    time.sleep(0.5)


def main():
    global update_dotime
    while 1:

        if li_do != []:
            operate_dcf()

        if do_kaig == True:
            read_kg(read_di_sta)

        if (datetime.datetime.now() - update_dotime).seconds > 4:
            read_dcf()
            update_dotime = datetime.datetime.now()


def socket_server():
    global li_do
    # 创建 socket 对象
    s = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM)
    # 获取本地主机名
    host = socket.gethostname()
    port = 8000 + com
    # 绑定端口
    s.bind((host, port))
    # 设置最大连接数，超过后排队
    s.listen(5)
    while True:
        # 建立客户端连接
        conn, addr = s.accept()
        recive_data = conn.recv(1024)
        recive_data = recive_data.decode('utf-8')

        print(com + 8000, '----收到指令', recive_data)
        # 这里收到
        li_do.append(recive_data)
        conn.send('ok'.encode('utf-8'))
        conn.close()


def socket_client(content):
    try:
        content = str(content)
        # 创建 socket 对象
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 获取本地主机名
        host = socket.gethostname()
        # 设置端口号
        port = 9000
        # 连接服务，指定主机和端口
        s.connect((host, port))
        # 接收小于 1024 字节的数据
        s.send(content.encode('utf-8'))

        print(com + 8000, '----发出指令', content)

        recive_data = s.recv(1024)
        recive_data = recive_data.decode('utf-8')

        s.close()
        return recive_data

    except:
        print('9000-----目标主机无法连接')


if __name__ == '__main__':

    # 基础的0606操作
    read_do_sta = '01 01 00 00 00 06 BC 08'
    read_di_sta = '01 02 00 00 00 06 F8 08'

    li_open = ['FE 05 00 00 FF 00 98 35', 'FE 05 00 01 FF 00 C9 F5', 'FE 05 00 02 FF 00 39 F5',
               'FE 05 00 03 FF 00 68 35',
               'FE 05 00 04 FF 00 D9 F4', 'FE 05 00 05 FF 00 88 34']
    li_close = ['FE 05 00 00 00 00 D9 C5', 'FE 05 00 01 00 00 88 05', 'FE 05 00 02 00 00 78 05',
                'FE 05 00 03 00 00 29 C5',
                'FE 05 00 04 00 00 98 04', 'FE 05 00 05 00 00 C9 C4']

    li = []
    li_do = []
    li_zaoy = []
    li_cunchu = []
    li_sqldata = []
    update_dotime = datetime.datetime.now()

    # a = sys.executable
    # b = a.split('\\')
    # get_com = False
    #
    # for i in range(len(b)):
    #     if 'exe' in b[i]:
    #         com = int(b[i].split('.')[0].split('_')[1].split('com')[1])
    #         get_com = True

    # 测试专用
    com = 23
    get_com = True

    if get_com == True:

        data_kg = get_kaig()

        if data_kg == 0:
            messagebox.showinfo('提示', '没有拿到开关信息，请注意！')

        ser = serial.Serial("COM" + str(com), 9600, 8)

        # 启动主函数
        t1 = threading.Thread(target=main)
        t1.start()

        # 启动服务器，接收指令，并侦测状态
        t2 = threading.Thread(target=socket_server)
        t2.start()

        # 启动服务器，接收指令，并侦测状态
        t3 = threading.Timer(10, get_kaig)
        t3.start()

        # 启动服务器，接收指令，并侦测状态
        t4 = threading.Timer(1, deal_sqldata)
        t4.start()

    else:

        messagebox.showinfo('提示', '没有找到dowhat信息，请注意！')


