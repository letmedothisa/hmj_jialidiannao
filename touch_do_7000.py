# -*- coding:utf-8 -*-
import datetime
import sys
import time
import tkinter
import tkinter.messagebox
import mysql_tengxun
import os
import socket
from tkinter import messagebox
import threading


def get_zaoyan():

    global li_fangguo
    global li_dianhuo
    global li
    # 去获取放锅的信息
    li_fangguo = []
    li_dianhuo = []

    now_time = datetime.datetime.now() + datetime.timedelta(hours=-4)

    sql = "SELECT * FROM fangguo WHERE creat_time > '%s' and guo_remove is NULL" % (now_time)

    data_fangguo = mysql_tengxun.mysql_getdata(sql)

    time.sleep(0.3)

    sql = "SELECT * FROM dcf_status"

    data_status = mysql_tengxun.mysql_getdata(sql)

    time.sleep(0.3)

    sql = "SELECT * FROM zao_setting"

    data_zao = mysql_tengxun.mysql_getdata(sql)



    if data_fangguo:
        for i in range(len(data_fangguo)):
            li_fangguo.append(data_fangguo[i][3] + data_fangguo[i][2] * 6)

    if data_status and data_zao:

        #i是灶眼的值
        for i in range(len(data_zao)):
            if data_zao[i][3]!=100:
                for j in range(len(data_status)):
                    if data_zao[i][3]==data_status[j][2]:
                        if data_status[j][data_zao[i][4]+3]==1:
                            li_dianhuo.append(i)

    li = []

    for i in range(12):
        if i in li_dianhuo:
            li.append('Green')
        elif i in li_fangguo:
            li.append('SkyBlue')
        else:
            li.append('LightSlateGray')

    print(li)
    global t2
    # 启动服务器，接收指令，并侦测状态
    t2 = threading.Timer(1, get_zaoyan)
    t2.start()


def killme():

    result = tkinter.messagebox.askokcancel(title='关闭重开', message='确定要关闭重开吗？')
    if result == True:
        python = sys.executable
        os.execl(python, python, *sys.argv)
    elif result==False:
        os._exit(0)

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
        recive_data=recive_data.decode('utf-8')
        li_do.append(recive_data)
        conn.send('ok'.encode('utf-8'))
        conn.close()

def socket_client(content):

    try:
        content=str(content)
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
        recive_data=s.recv(1024)
        recive_data = recive_data.decode('utf-8')
        s.close()
        return recive_data

    except:
        print('目标主机9000---端口没有在服务中')


def choose_one(choose_one, zaotai, zaoyan, dialog_box):


    if choose_one == 1:

        dialog_box.destroy()
        print('选择了确定')
        zaoyan_num = zaotai * 6 + zaoyan

        content = str(zaoyan_num)
        data_recive = socket_client(content)
        if data_recive != 'ok':
            tkinter.messagebox.showerror(title='警告', message='操作电磁阀失败')
    else:

        dialog_box.destroy()

def func(zaotai, zaoyan):

    dialog_box = tkinter.Tk()

    # 弹出对话框
    dialog_box.title("是否确认操作")
    dialog_box.resizable(0, 0)
    dialog_box.attributes("-topmost", 1)
    dialog_box.geometry("420x250+300+300")
    button1 = tkinter.Button(dialog_box, text="确定", font=('黑体', 20), command=lambda: choose_one(1,zaotai,zaoyan,dialog_box), width=12,
                             height=4, bg='LightSkyBlue')
    button1.place(relx=0.05, rely=0.2)

    button2 = tkinter.Button(dialog_box, text="取消", font=('黑体', 20), command=lambda: choose_one(0,zaotai,zaoyan,dialog_box), width=12,
                             height=4, bg='LightSlateGray')

    button2.place(relx=0.55, rely=0.2)

    threading.Timer(5, timeToClose, args=(dialog_box,)).start()

    dialog_box.mainloop()



def timeToClose(dialog_box):
    try:
        dialog_box.destroy()
    except:
        print('窗口已经被点击了')
def main_surface():

    global li_surface

    if li_surface!=li:
        li_surface=li

        # 创建按钮
        button1 = tkinter.Button(win, text="按钮", command=lambda: func(1, 5), width=20, height=13, bg=li[11])

        button1.place(relx=0.05, rely=0.1)

        button2 = tkinter.Button(win, text="按钮", command=lambda: func(1, 3), width=20, height=13, bg=li[9])
        button2.place(relx=0.2, rely=0.1)

        button3 = tkinter.Button(win, text="按钮", command=lambda: func(1, 1), width=20, height=13, bg=li[7])
        button3.place(relx=0.35, rely=0.1)

        button4 = tkinter.Button(win, text="按钮", command=lambda: func(1, 4), width=20, height=13, bg=li[10])

        button4.place(relx=0.05, rely=0.5)

        button5 = tkinter.Button(win, text="按钮", command=lambda: func(1, 2), width=20, height=13, bg=li[8])
        button5.place(relx=0.2, rely=0.5)

        button6 = tkinter.Button(win, text="按钮", command=lambda: func(1, 0), width=20, height=13, bg=li[6])
        button6.place(relx=0.35, rely=0.5)

        # 创建按钮
        button7 = tkinter.Button(win, text="按钮", command=lambda: func(0, 5), width=20, height=13, bg=li[5])

        button7.place(relx=0.53, rely=0.1)

        button8 = tkinter.Button(win, text="按钮", command=lambda: func(0, 3), width=20, height=13, bg=li[3])
        button8.place(relx=0.68, rely=0.1)

        button9 = tkinter.Button(win, text="按钮", command=lambda: func(0, 1), width=20, height=13, bg=li[1])
        button9.place(relx=0.83, rely=0.1)

        button10 = tkinter.Button(win, text="按钮", command=lambda: func(0, 4), width=20, height=13, bg=li[4])

        button10.place(relx=0.53, rely=0.5)

        button11 = tkinter.Button(win, text="按钮", command=lambda: func(0, 2), width=20, height=13, bg=li[2])
        button11.place(relx=0.68, rely=0.5)

        button12 = tkinter.Button(win, text="按钮", command=lambda: func(0, 0), width=20, height=13, bg=li[0])
        button12.place(relx=0.83, rely=0.5)

        button13 = tkinter.Button(win, text="关闭程序重开", command=killme, width=20, height=3, bg='LightSlateGray')
        button13.place(relx=0.83, rely=0.9)

        win.attributes("-topmost", 2)
        win.after(2000,main_surface)
    else:
        win.after(2000,main_surface)
if __name__ == '__main__':

    #获取端口号
    # a = sys.executable
    # b = a.split('\\')
    # get_com = False
    #
    # for i in range(len(b)):
    #     if 'exe' in b[i]:
    #         control_port = int(b[i].split('.')[0].split('_')[2])
    #         get_com = True

    #测试专用
    control_port=7000
    get_com=True

    if get_com==True:

        li = []
        li_surface=[]
        for i in range(12):
                li.append('LightSlateGray')

        # 启动服务器，接收指令，并侦测状态
        t2 = threading.Timer(1,get_zaoyan)
        t2.start()

        #主画布
        win = tkinter.Tk()
        win.title("灶台点火程序")
        win.geometry("1000x650+1+1")
        win.after(2000,main_surface)

        win.mainloop()


    else:
        messagebox.showinfo('提示', '没有找到dowhat信息，请注意！')