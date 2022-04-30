# -*- coding:utf-8 -*-
# 导入 socket 模块
import datetime
import socket

li=['open',1]

def client():
    # 创建 socket 对象
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 获取本地主机名
    host = socket.gethostname()
    # 设置端口号
    port = 9999
    # 连接服务，指定主机和端口
    s.connect((host, port))
    # 接收小于 1024 字节的数据
    s.send(str(li).encode('utf-8'))
    print(datetime.datetime.now())
    recive_data = s.recv(1024).decode('utf-8')
    s.close()
    return recive_data

data_recive=client()
print(data_recive)