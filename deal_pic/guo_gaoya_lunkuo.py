# -*- coding:utf-8 -*-
import cv2


def read_img(filename):
    img = cv2.imread(filename, 1)
    return img


def gaussian_blur(img):
    gaussian_img = cv2.GaussianBlur(img, (3, 3), 3)
    return gaussian_img


def gray_procession(img):
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return gray_img


def threshold_procession(img, threshold):
    _, threshold_img = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)
    return threshold_img


def get_num(img1,img2,li_outline,lunkuo_small,lunkuo_big):


    yaji_outline1=[]

    contours, hierarchy = cv2.findContours(img1, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    x = []
    y = []
    for i in range(len(contours)):

        sum_x = 0
        sum_y = 0
        max_x=0
        min_x=100000
        max_y=0
        min_y=100000
        k=0


        for j in range(len(contours[i])):
            if (li_outline[0] + li_outline[2]) > contours[i][j][0][0] > li_outline[0] and (
                    li_outline[1] + li_outline[3]) > contours[i][j][0][1] > li_outline[1]:
                k += 1
                sum_x += contours[i][j][0][0]
                sum_y += contours[i][j][0][1]
                x.append(contours[i][j][0][0])
                y.append(contours[i][j][0][1])


                if contours[i][j][0][0]>max_x:
                    max_x=contours[i][j][0][0]
                if contours[i][j][0][0]<min_x:
                    min_x=contours[i][j][0][0]
                if contours[i][j][0][1]>max_y:
                    max_y=contours[i][j][0][1]
                if contours[i][j][0][1]<min_y:
                    min_y=contours[i][j][0][1]

        if len(contours[i])==k and lunkuo_big>k>lunkuo_small:
            center_x=int((min_x+max_x)/2)
            center_y=int((min_y+max_y)/2)
            yaji_outline_1=[]
            yaji_outline_1.append(k)
            yaji_outline_1.append(min_x)
            yaji_outline_1.append(max_x)
            yaji_outline_1.append(min_y)
            yaji_outline_1.append(max_y)
            yaji_outline_1.append(center_x)
            yaji_outline_1.append(center_y)
            yaji_outline1.append(yaji_outline_1)

    print(yaji_outline1)

    cv2.drawContours(img2, contours, -1, (0, 0, 255), 3)
    cv2.namedWindow('final_img', 1)
    cv2.imshow('final_img', img2)
    cv2.imwrite('123.png',img2)
    cv2.waitKey()
    return yaji_outline1



def main(li,filepic,standard,lunkuo_small,lunkuo_big):

    img = read_img(filepic)
    gaussian_img = gaussian_blur(img)
    gray_img = gray_procession(gaussian_img)
    threshold_img = threshold_procession(gray_img, standard)
    outline_num=get_num(threshold_img,img,li,lunkuo_small,lunkuo_big)
    return outline_num

if __name__ == '__main__':
    main()