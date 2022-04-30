# -*- coding:utf-8 -*-

import cv2

def get_hsv(file_pic,x,y,x_long,y_long):

    image = cv2.imread(file_pic)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h = []
    s = []
    v = []
    i = 0
    j = 0
    q = x
    place=[]
    while i < y_long:
        while j < x_long:
            place_1=[]
            j += 1
            get_color = hsv[y, x]
            v.append(get_color[2])
            s.append(get_color[1])
            h.append(get_color[0])
            place_1.append(x)
            place_1.append(y)
            place.append(place_1)

            x += 1

        j = 0
        x = q
        i += 1
        y += 1

    return(h,s,v,place)

if __name__=='__main__':
    get_hsv()