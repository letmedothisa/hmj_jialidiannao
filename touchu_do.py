# -*- coding:utf-8 -*-
import datetime
import sys
import tkinter
import tkinter.messagebox
import mysql_tengxun
import time
import serial
import os
import binascii


data_fangguo = []
zaoyan_timelong = []
data_fangguo_cunchu = []
li_sqldata = []
data_yaji_cunchu = []
allready_touchu = False

li_open = ['FE 05 00 00 FF 00 98 35', 'FE 05 00 01 FF 00 C9 F5', 'FE 05 00 02 FF 00 39 F5', 'FE 05 00 03 FF 00 68 35',
           'FE 05 00 04 FF 00 D9 F4', 'FE 05 00 05 FF 00 88 34']
li_close = ['FE 05 00 00 00 00 D9 C5', 'FE 05 00 01 00 00 88 05', 'FE 05 00 02 00 00 78 05', 'FE 05 00 03 00 00 29 C5',
            'FE 05 00 04 00 00 98 04', 'FE 05 00 05 00 00 C9 C4']
li_status = ['FE 01 00 00 00 01 E9 C5', 'FE 01 00 01 00 01 B8 05', 'FE 01 00 02 00 01 48 05', 'FE 01 00 03 00 01 19 C5',
             'FE 01 00 04 00 01 A8 04', 'FE 01 00 05 00 01 F9 C4']

li_cunchu = [[0, 0, 0], [1, 0, 0], [2, 0, 0], [3, 0, 0], [4, 0, 0], [5, 0, 0], [6, 0, 0], [7, 0, 0], [8, 0, 0],
             [9, 0, 0], [10, 0, 0], [11, 0, 0]]

li_duiying = []

with open('config.txt', 'r') as f:
    a = f.readlines()
    for i in range(len(a)):
        b = a[i].split(' ')
        if b[0] == 'control_dcf':
            li_1 = []
            li_1.append(int(b[1].split('=')[1]))
            li_1.append(int(b[2].split('=')[1]))
            li_1.append(int(b[3].split('=')[1]))
            li_1.append(int(b[4].split('=')[1]))
            li_1.append(int(b[5].replace('\n', '').split('=')[1]))
            li_duiying.append(li_1)


def get_status(operate_num, com):
    get_result = 0
    try:
        ser = serial.Serial("COM" + str(com), 9600, 8)
        if ser.isOpen():
            result = ser.write(bytes.fromhex(operate_num))

            time.sleep(0.5)
            len_return_data = ser.inWaiting()

            if len_return_data > 0:
                read_data = ser.read(len_return_data)
                get_result = str(binascii.b2a_hex(read_data))[2:-1]
        ser.close()

    except:
        print('open_serial_error')

    return get_result


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

    win.after(1000, deal_sqldata)


def close_dianhuo():
    global li_cunchu

    for i in range(12):

        if li_cunchu[i][2] != 0:
            if (datetime.datetime.now() - li_cunchu[i][2]).seconds > 6:
                zaoyan_num = li_cunchu[i][0]
                operate_num = li_duiying[zaoyan_num][3]
                com_sz = li_duiying[zaoyan_num][4]
                jieguo = operate(li_close[operate_num], com_sz)
                if jieguo == 8:
                    read_data = get_status(li_status[operate_num], com_sz)
                    if read_data != 0:
                        print(read_data)
                        if read_data == 'fe010100619c':
                            print('到时间关点火成功')
                            li_cunchu[zaoyan_num][2] = 0

    win.after(1350, close_dianhuo)


def closezao():

    global li_cunchu
    global li_sqldata

    for i in range(12):

        if li_cunchu[i][1] != 0:
            if zaoyan_timelong:
                time_long = int(zaoyan_timelong[li_cunchu[i][0]][3]) * 60
            else:
                time_long = 1080

            # print('灶眼：' + str(li_cunchu[i][0]) + '----点火时长总计：' + str(time_long))

            if (datetime.datetime.now() - li_cunchu[i][1]).seconds > time_long:

                zaoyan_num = li_cunchu[i][0]
                operate_num = li_duiying[zaoyan_num][1]
                com_sz = li_duiying[zaoyan_num][2]
                jieguo = operate(li_close[operate_num], com_sz)

                if jieguo == 8:

                    # 判断关火成功
                    read_data = get_status(li_status[operate_num], com_sz)
                    if read_data != 0:
                        if read_data == 'fe010100619c':
                            print('到时间关火成功')

                            # 标记位置0
                            li_cunchu[zaoyan_num][1] = 0

                            # 数据上传到服务器
                            yaji_long = round((datetime.datetime.now() - li_cunchu[zaoyan_num][1]).seconds / 60, 2)
                            sql = "update shangqi_2 set yaji_long = '%s',guanhuo_time ='%s' where yaji_time = '%s'" % (
                                yaji_long, datetime.datetime.now(), li_cunchu[zaoyan_num][1])

                            li_sqldata.append(sql)

    win.after(1000, closezao)


def get_timelong():
    global zaoyan_timelong
    sql = "SELECT * FROM zaoyan_timelong"

    while 1:
        try:
            zaoyan_timelong = mysql_tengxun.mysql_getdata(sql)
            break

        except:
            time.sleep(1)
            print('get fangguo data error')
            break

    win.after(30000, get_timelong)


def operate(operate_dcf, com):
    len_return_data = 0
    try:
        ser = serial.Serial("COM" + str(com), 9600, 8)
        if ser.isOpen():
            result = ser.write(bytes.fromhex(operate_dcf))
            time.sleep(0.5)
            len_return_data = ser.inWaiting()
        ser.close()

    except:
        print('open_serial_error')

    return len_return_data


def get_fangguo():

    now_time = datetime.datetime.now() + datetime.timedelta(hours=-6)
    sql = "SELECT * FROM fangguo WHERE fangguo.creat_time > '%s' and fangguo.guo_remove IS NULL" % (now_time)
    data_item_fangguo = []
    while 1:
        try:
            data_item_fangguo = mysql_tengxun.mysql_getdata(sql)
            break

        except:
            time.sleep(1)
            print('get fangguo data error')
            break

    return data_item_fangguo


def killme():
    result = tkinter.messagebox.askokcancel(title='关闭重开', message='确定要关闭重开吗？')
    if result == True:
        python = sys.executable
        os.execl(python, python, *sys.argv)

def func(zaotai, zaoyan):
    # 弹出对话框
    global li_cunchu

    win_tishi = tkinter.Toplevel()
    win_tishi.title("是否确认操作")
    win_tishi.configure(bg='Snow')
    win_tishi.resizable(0, 0)
    win_tishi.overrideredirect(1)
    win_tishi.attributes("-topmost", 1)

    win_tishi.geometry("420x250+300+300")
    button1 = tkinter.Button(win_tishi, text="确定", font=('黑体', 20), command=lambda: choose_one(1,zaotai,zaoyan,win_tishi), width=12,
                             height=4, bg='limegreen')
    button1.place(relx=0.05, rely=0.2)
    button2 = tkinter.Button(win_tishi, text="取消", font=('黑体', 20), command=lambda: choose_one(0,zaotai,zaoyan,win_tishi), width=12,
                             height=4, bg='silver')

    button2.place(relx=0.55, rely=0.2)
    win_tishi.mainloop()


def choose_one(what,zaotai,zaoyan,win_tishi):

    global allready_touchu
    global li_sqldata


    if what == 1:


        win_tishi.destroy()
        print('选择了确定')
        zaoyan_num = zaotai * 6 + zaoyan
        operate_num = li_duiying[zaoyan_num][1]
        com_sz = li_duiying[zaoyan_num][2]
        dianhuo_operate_num = li_duiying[zaoyan_num][3]
        dianhuo_com_xz = li_duiying[zaoyan_num][4]
        jieguo = 0
        jieguo_dianhuo = 0

        if li_cunchu[zaoyan_num][1] == 0:

            if int(com_sz) != 100:
                jieguo = operate(li_open[operate_num], com_sz)


            if int(dianhuo_com_xz) != 100:
                jieguo_dianhuo = operate(li_open[dianhuo_operate_num], dianhuo_com_xz)

            if jieguo == 8:

                read_data = get_status(li_status[operate_num], com_sz)

                if read_data != 0:

                    if read_data != 'fe010100619c':

                        print('打开电磁阀成功')
                        dianhuo_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        dianhuo_time = datetime.datetime.strptime(dianhuo_time, '%Y-%m-%d %H:%M:%S')
                        li_cunchu[zaoyan_num][1] = dianhuo_time


                        sql = "insert into shangqi_2 set zaotai = '%s',zaoyan = '%s',creat_time = '%s',yaji_time = '%s'" % (
                            zaotai, zaoyan, dianhuo_time, dianhuo_time)

                        li_sqldata.append(sql)

                        sql = "update shangqi_2 set yaji_long = '%s',guanhuo_time ='%s' where zaotai = '%s' and zaoyan = '%s' and yaji_time < '%s'" % (
                            0, datetime.datetime.now(), zaotai, zaoyan,
                            datetime.datetime.now() + datetime.timedelta(seconds=-5))
                        li_sqldata.append(sql)

                    else:
                        tkinter.messagebox.showerror(title='警告', message='操作电磁阀失败')
            else:
                tkinter.messagebox.showerror(title='警告', message='操作电磁阀失败')

            if jieguo_dianhuo == 8:

                read_data = get_status(li_status[operate_num], com_sz)

                if read_data != 0:

                    if read_data != 'fe010100619c':
                        dianhuo_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        dianhuo_time = datetime.datetime.strptime(dianhuo_time, '%Y-%m-%d %H:%M:%S')
                        li_cunchu[zaoyan_num][2] = dianhuo_time
                        print('点火设备点火成功')
                else:
                    tkinter.messagebox.showerror(title='警告', message='点火设备点火失败')

        else:

            jieguo = 0
            if int(com_sz) != 100:
                jieguo = operate(li_close[operate_num], com_sz)
            if jieguo == 8:

                read_data = get_status(li_status[operate_num], com_sz)

                if read_data != 0:
                    if read_data == 'fe010100619c':
                        print('关火成功')

                        yaji_long = round((datetime.datetime.now() - li_cunchu[zaoyan_num][1]).seconds / 60, 2)

                        sql = "update shangqi_2 set yaji_long = '%s',guanhuo_time ='%s' where yaji_time = '%s'" % (
                            yaji_long, datetime.datetime.now(), li_cunchu[zaoyan_num][1])

                        li_sqldata.append(sql)

                        li_cunchu[zaoyan_num][1] = 0

    else:

        win_tishi.destroy()


def get_zaoyan():
    global data_fangguo_cunchu
    global data_yaji_cunchu
    # 去获取放锅的信息

    data_fangguo = []
    data_yaji = []

    data_item_fangguo = get_fangguo()

    if data_item_fangguo:
        for i in range(len(data_item_fangguo)):
            data_fangguo.append(data_item_fangguo[i][3] + data_item_fangguo[i][2] * 6)

    for i in range(12):
        if li_cunchu[i][1] != 0:
            data_yaji.append(li_cunchu[i][0])

    if data_fangguo != data_fangguo_cunchu or data_yaji != data_yaji_cunchu:

        data_fangguo_cunchu = data_fangguo
        data_yaji_cunchu = data_yaji

        li = []

        for i in range(12):
            if i in data_yaji:
                li.append('Green')
            elif i in data_fangguo:
                li.append('SkyBlue')
            else:
                li.append('Gray')

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

        button13 = tkinter.Button(win, text="关闭程序重开", command=killme, width=20, height=3, bg='Gray')
        button13.place(relx=0.83, rely=0.9)

        win.attributes("-topmost", 2)
        win.overrideredirect(1)
        win.after(1000, get_zaoyan)

    else:
        win.after(1000, get_zaoyan)


if __name__ == '__main__':
    win = tkinter.Tk()
    get_timelong()
    win.title("灶台点火程序")
    win.geometry("1000x700+1+1")
    win.after(1000, get_zaoyan)
    win.after(1000, closezao)
    win.after(1000, deal_sqldata)
    win.after(30000, get_timelong)
    win.after(1350, close_dianhuo)
    win.mainloop()
