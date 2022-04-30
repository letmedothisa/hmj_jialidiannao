import socket
import datetime
serversocket = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM)
# 获取本地主机名
host = socket.gethostname()
port = 9999
li_do=[]
# 绑定端口
serversocket.bind((host, port))
# 设置最大连接数，超过后排队
serversocket.listen(5)
while True:
    # 建立客户端连接
    clientsocket, addr = serversocket.accept()
    recive_data = clientsocket.recv(1024)
    recive_data = recive_data.decode('utf-8')
    recive_data=recive_data.replace('[','').replace(']','').split(',')
    li_do.append(recive_data)
    clientsocket.send('ok'.encode('utf-8'))
    clientsocket.close()