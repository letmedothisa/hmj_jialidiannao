import serial
import threading
import mysql_tengxun
import time
import datetime

def update_data():

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

    global t1
    #启动上传数据库
    t1=threading.Timer(5,update_data)
    t1.start()

def read_water():

    global water_num
    global changge
    global fangshui_times
    global last_num

    ser = serial.Serial("COM" + str(com), 9600, 8)
    if ser.isOpen():
        result = ser.write("#015".encode())
        print(result)
        time.sleep(0.5)
        count = ser.inWaiting()
        if count != 0:
            read_data = ser.read(count)
            read_data = str(read_data[2:-1], encoding='utf-8')
            A0_data = int(read_data.split(",")[0])
            B0_data = int(read_data.split(",")[1])

            if B0_data != water_num:
                changge = True
                water_num=B0_data
            elif B0_data==water_num and changge==True:
                water_quantity=A0_data-last_num
                last_num=A0_data
                changge = False

                # 数据上传到服务器
                sql = "insert into water_num set creat_time = '%s',water_num ='%s',water_quantity='%s'" % (datetime.datetime.now(), water_num,water_quantity)
                li_sqldata.append(sql)

    ser.close()
    global t2
    #启动读取串口数据
    t2=threading.Timer(0.4,read_water)
    t2.start()

if __name__=="__main__":

    com = 23
    water_num = 0
    changge = False
    last_num = 0
    li_sqldata=[]

    #启动上传数据库
    t1=threading.Timer(5,update_data)
    t1.start()

    #启动读取串口数据
    t2=threading.Timer(0.4,read_water)
    t2.start()