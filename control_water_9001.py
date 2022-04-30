# -*- coding:utf-8 -*-
import threading
import time
import socket
from tkinter import messagebox
import mysql_tengxun
import datetime
import serial

# "水量"的串口
com_sl = 23
ser = serial.Serial("COM" + str(com_sl), 9600, 8)

#这里需要按照设备返回的数据顺序，要把水量和关水的电池阀对应起来，目前是2口的配置
li=[[300,4],[1400,5]]

#把最初的和最近的赋值
li_ini=[0,0]
li_last=[0,0]

def get_setting():


    global li_dcf
    global li_kaig
    global li_waternum
    global li_zaoy
    data_sql = 0

    sql = "select * from zao_setting where port='%s'"%(control_port)

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
        li_kaig = []
        li_waternum=[]
        li_zaoy=[]

        for i in range(len(data_sql)):
            # 所有配置搞好
            li_dcf_1 = []
            li_dcf_1.append(data_sql[i][3])
            li_dcf_1.append(data_sql[i][4])
            li_dcf.append(li_dcf_1)
            li_kaig_1 = []
            li_kaig_1.append(data_sql[i][7])
            li_kaig_1.append(data_sql[i][8])
            li_kaig.append(li_kaig_1)

            li_zaoy.append(data_sql[i][2])
            li_waternum.append(data_sql[i][10])

        return data_sql

    global t5
    # 启动服务器，接收指令，并侦测状态
    t5 = threading.Timer(10, get_setting)
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
        print(control_port,'----接到命令', recive_data)
        conn.send('ok'.encode('utf-8'))
        conn.close()


def socket_client(com, content):
    try:
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
        print(control_port,'----发出命令', content)
        recive_data = s.recv(1024)
        recive_data = recive_data.decode('utf-8')
        s.close()
        return recive_data
    except:
        print(8000+com,'----端口发送数据没有成功')


def open_water():

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

            equip_position=data_sql[0][11]

            if com_dcf != 100 and com_dcf != None:

                pos_dcf = data_sql[0][4]

                if li_cunchu[equip_position][1] == 0:
                    operate = 'open'
                else:
                    operate = 'close'

                content = operate + ',' + str(pos_dcf)
                data_dcf = socket_client(com_dcf, content)

                if data_dcf == 'ok':

                    if operate == 'open':

                        print(zaoyan,'----开水成功')
                        dianhuo_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        dianhuo_time = datetime.datetime.strptime(dianhuo_time, '%Y-%m-%d %H:%M:%S')

                        li_cunchu[equip_position][1] = dianhuo_time

                        sql = "insert into zao_record set zaoyan = '%s',dianhuo_time = '%s'" % (
                            zaoyan, dianhuo_time)

                        li_sqldata.append(sql)

                    elif operate == 'close':

                        print(zaoyan,'----关水成功')

                        # 数据上传到服务器
                        yaji_long = round((datetime.datetime.now() - li_cunchu[equip_position][1]).seconds / 60, 2)

                        sql = "update zao_record set cook_long = '%s',guanhuo_time ='%s' where dianhuo_time = '%s'" % (
                            yaji_long, datetime.datetime.now(), li_cunchu[equip_position][1])
                        li_sqldata.append(sql)

                        li_cunchu[equip_position][1] = 0

                        del li_do[0]

                    else:
                        del li_do[0]

    global t2
    # 启动点火线程
    t2 = threading.Timer(0.5, open_water)
    t2.start()


def close_water():

    global li_cunchu

    if ser.isOpen():

        result = ser.write("#015".encode())

        if result != 0:

            times=0

            while 1:

                times+=1

                time.sleep(0.01)

                count = ser.inWaiting()

                if count != 0:

                    read_data = ser.read(count)

                    read_data = str(read_data[0:-1], encoding='utf-8').replace('!', '').replace("\r", "")

                    list_data = read_data.split(",")

                    break

                if times==100:
                    print('没有获取数据')
                    break


    for i in range(len(li_cunchu)):

        if li_cunchu[i][1] != 0:

            if int(list_data[i]) != 0 and li_ini[i] == 0:
                li_ini[i]=int(list_data[i])

            elif int(list_data[i]) != li_ini[i] and int(list_data[i]) != li_last[i]:

                water_quantity = int(list_data[i]) - li_ini[i]

                li_last[i] = int(list_data[i])

                if water_quantity > li_waternum[i]:

                    com_dcf=li_dcf[i][0]
                    pos_dcf=li_dcf[i][1]

                    operate = 'close'
                    content = operate + ',' + str(pos_dcf)
                    data_dcf = socket_client(com_dcf, content)

                    if data_dcf == 'ok':

                        # 数据上传到服务器
                        yaji_long = round((datetime.datetime.now() - li_cunchu[i][1]).seconds / 60, 2)

                        sql = "update zao_record set cook_long = '%s',guanhuo_time ='%s' where dianhuo_time = '%s'" % (
                            yaji_long, datetime.datetime.now(), li_cunchu[i][1])

                        li_sqldata.append(sql)

                        li_cunchu[i][1] = 0
                        li_ini[i] = 0
                        li_last[i] = 0


        global t3
        # 启动点火线程
        t3 = threading.Timer(0.5, close_water)
        t3.start()


if __name__ == '__main__':

    li_cunchu = []
    li_dcf = []
    li_waternum=[]
    li_kaig = []
    li_duration = []
    li_do = []
    li_sqldata = []
    li_ini=[]

    # a = sys.executable
    # b = a.split('\\')
    # get_com = False
    #
    # for i in range(len(b)):
    #     if 'exe' in b[i]:
    #         control_port = int(b[i].split('.')[0].split('_')[2])
    #         get_com = True

    # 测试专用
    control_port = 9001
    get_com = True

    if get_com == True:

        data_zao = get_setting()

        if data_zao == 0:
            messagebox.showinfo('提示', '没拿到灶台相关配置信息，请关注！')
        else:
            for i in range(len(data_zao)):
                li_cunchu.append([data_zao[i][11], 0, 0])
                li_ini.append(0)
                li_last.append(0)

                # 启动主函数

        t1 = threading.Thread(target=socket_server)
        t1.start()

        # 启动点火线程
        t2 = threading.Timer(0.5, open_water)
        t2.start()

        # 启动服务器，接收指令，并侦测状态
        t3 = threading.Timer(0.5, close_water)
        t3.start()

        # 启动服务器，接收指令，并侦测状态
        t4 = threading.Timer(1, deal_sqldata)
        t4.start()

        # 启动服务器，接收指令，并侦测状态
        t5 = threading.Timer(10, get_setting)
        t5.start()



