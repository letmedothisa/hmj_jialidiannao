# -*- coding:utf-8 -*-
import cv2
import datetime
import os
import sys

#通过获得exe的名称来决定录像的一些配置情况
a=sys.executable
b=a.split('\\')
for i in range(len(b)):
    if 'exe' in b[i]:
        dowhat_1=b[i].split('.')
        dowhat=dowhat_1[0]


#获取摄像头参数,以及图片的存储路径
with open('config.txt', 'r') as f:
    a = f.readlines()
    for i in range(len(a)):
        b = a[i].split(' ')
        if b[0] == dowhat:
            camera_num = int(b[1].split('=')[1])
            picture_path=b[3].split('=')[1]
            cap_rate=int(b[2].split('=')[1])

#基本录像配置
cap = cv2.VideoCapture(camera_num, cv2.CAP_DSHOW)
WIDTH = 1920
HEIGHT = 1080
FPS = 10
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
cap.set(cv2.CAP_PROP_FPS, 10)
fourcc = cv2.VideoWriter_fourcc(*'XVID')

while 1:
    #看看是否有新的摄像头参数配置
    with open('config.txt', 'r') as f:
        a = f.readlines()
        for i in range(len(a)):
            b = a[i].split(' ')
            if b[0] == dowhat:

                #重新拿到摄像头配置,并确定截图频率和录像的目录
                camera_num_check = int(b[1].split('=')[1])
                picture_path = b[3].split('=')[1]
                cap_rate = int(b[2].split('=')[1])
                file_path_pic=picture_path+datetime.datetime.now().strftime('%Y-%m-%d')+'_pic/'

    #看看摄像头有没有更新
    if camera_num!=camera_num_check:
        cap = cv2.VideoCapture(camera_num_check, cv2.CAP_DSHOW)
        # 基本录像配置
        WIDTH = 1920
        HEIGHT = 1080
        FPS = 10
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
        cap.set(cv2.CAP_PROP_FPS, 10)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')

    #看看图片和录像的目录是否存在
    if not os.path.exists(file_path_pic):
        os.makedirs(file_path_pic)


    start_luxiang = datetime.datetime.now()
    count=0
    while 1:
        count+=1
        rep, frame = cap.read()

        if (datetime.datetime.now() - start_luxiang).seconds >= 60:
            break

        if cap_rate and count%cap_rate==0:
            FILE_PIC=file_path_pic+datetime.datetime.now().strftime('%H-%M-%S')+datetime.datetime.now().strftime('-%f')+'.png'
            cv2.imwrite(FILE_PIC, frame)