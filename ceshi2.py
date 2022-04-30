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

def func(zaotai,zaoyan):
    print(zaotai,zaoyan)

win = tkinter.Tk()
win.title("灶台点火程序")
win.geometry("1000x550+1+1")
# 创建按钮
# 创建按钮
li=['Gray','Gray','Gray','Gray','Gray','Gray','Gray','Gray','Gray','Gray','Gray','Gray']

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


win.mainloop()
