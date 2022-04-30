import datetime

import serial
import binascii,time


def get_temper(com):

    li_wendu = []
    li_wendu_10 = []
    # 配置串口基本参数并建立通信
    ser = serial.Serial("COM"+str(com), 9600, 8, "E", timeout=50, stopbits=1)

    # 数据帧
    a = '00 03 00 28 00 08 C5 D5'

    # 简单的发送16进制字符
    # ser.write(b'\xFE\xFE\xFE')
    # 但是上面的方法不够优雅，需要自己添加\x，非常麻烦，于是使用下面这个方法
    d = bytes.fromhex(a)

    # 串口发送数据
    result = ser.write(d)

    # 停止、等待数据，这一步非常关键。timeout压根没用

    time.sleep(1)
    count = ser.inWaiting()

    print(count)

    # 数据的接收
    if count > 0:
        data = ser.read(count)
        if data != b'':
            # 将接受的16进制数据格式如b'h\x12\x90xV5\x12h\x91\n4737E\xc3\xab\x89hE\xe0\x16'
            #                      转换成b'6812907856351268910a3437333745c3ab896845e016'
            #                      通过[]去除前后的b'',得到我们真正想要的数据
            wendu = str(binascii.b2a_hex(data))[8:-1]

    wendu = list(wendu)

    for i in range(8):
        li_wendu.append(str(wendu[i * 4]) + str(wendu[i * 4 + 1]) + str(wendu[i * 4 + 2]) + str(wendu[i * 4 + 3]))
    for i in range(len(li_wendu)):
        li_wendu_10.append(int(str(li_wendu[i]), 16) / 10)

    # 关闭串口
    ser.close()
    return li_wendu_10


li=[]

with open('config.txt', 'r') as f:
    a = f.readlines()
    for i in range(len(a)):
        b = a[i].split(' ')
        if b[0] == 'get_temperature':
            li_temp_1 = []
            li_temp_1.append((b[1]).split('=')[1])
            li_temp_1.append(int((b[2]).split('=')[1]))
            li_temp_1.append(int((b[3]).split('=')[1]))
            li_temp_1.append(int((b[4].replace("\n","")).split('=')[1]))
            li.append(li_temp_1)

while 1:
    li_temp=get_temper(li[0][4])
    for i in range(len(li)):
        sql = "insert into all_temperature set creat_time = '%s',temperature = '%s',device = '%s',device_number = '%s'" % (datetime.datetime.now(),li_temp[li[i][3]],li[i][1],li[i][2])
        while 1:
            try:
                mysql_tengxun.mysql_db(sql)
                break
            except:
                time.sleep(1)
                continue
                print('insert___date__error')

    time.sleep(1)