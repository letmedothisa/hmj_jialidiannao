# -*- coding:utf-8 -*-
import getall_basedata
import datetime
import mysql_dbggg
import time
import matplotlib.pyplot as plt
import mysql_tengxun


def mifan_on(hours_before):

    data=[]
    jirou_guo = 0
    try:
        data = getall_basedata.get_data(hours_before, 'shangqi2', 'yaji_time')
    except:
        time.sleep(1)
        print('get_shangqi_data_error')
    if data:
        for i in range(len(data)):
            if data[i][5] == None and (datetime.datetime.now() - data[i][4]).seconds > 320:
                jirou_guo += 1

    return jirou_guo


def mifan_done(hours_before,hours_after):

    jirou_guo = 0
    sql = "SELECT * FROM zhengfan where zhengfan.dianhuo_time> '%s' and zhengfan.dianhuo_time<'%s'" % (hours_before,hours_after)
    try:
        data = mysql_tengxun.mysql_getdata(sql)
        if data:
            for i in range(len(data)):
                if data[i][5] != None and data[i][9] > 15:
                    jirou_guo += 1

        return jirou_guo
    except:
        time.sleep(1)
        print('get jiroudone data error')
        return jirou_guo



def get_dingdan_mifan(hours_before_jiangbo,hours_after_jiangbo):
    jirou_weight = 0
    mifan_num = 0
    data_dingdan = []
    # 配置数据库信息,注意，只拿了第一个灶眼的炖土豆信息
    sqlset = "SELECT * FROM orderitems WHERE orderitems.create_date > '%s' and orderitems.create_date < '%s'ORDER BY orderitems.create_date ASC" % (hours_before_jiangbo,hours_after_jiangbo)
    # 拿数据，干活
    try:
        data_dingdan = mysql_dbggg.mysql_db(sqlset)
    except:
        time.sleep(0.5)
        print('getdata_error')

    if data_dingdan:
        for data1 in data_dingdan:
            if '两份黄焖鸡大份' in data1[9]:
                jirou_weight += 0.76 * int(data1[7]) * 2
                mifan_num += 2 * int(data1[7])
            elif '黄焖鸡大份' in data1[9]:
                jirou_weight += 0.76 * int(data1[7])
                mifan_num += 1 * int(data1[7])
            elif '黄焖鸡小份' in data1[9]:
                jirou_weight += 0.56 * int(data1[7])
                mifan_num += 1 * int(data1[7])
            elif '米饭' in data1[9]:
                mifan_num += 1 * int(data1[7])

    return mifan_num


if __name__ == '__main__':
    # 初始化图表
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  #

    fig, ax = plt.subplots(figsize=(13, 5))
    plt.title("压鸡数量", fontsize=26)  # 图形标题
    ax.set_xticks([])
    ax.set_yticks([])
    fig.canvas.manager.window.wm_geometry('+5+750')
    plt.pause(0.2)
    save_time = datetime.datetime.now()
    li = []
    li_jirou = []
    li_jirou_gf = []
    color_jirou = []
    color_jirou_gf = []
    jichu_jirou = 0
    jirou_time = datetime.datetime.now()
    jirou_gf_time = datetime.datetime.now()+datetime.timedelta(seconds=-30)

    while 1:

        timedone = int(datetime.datetime.now().strftime('%H%M'))
        timehour = int(datetime.datetime.now().strftime('%H'))

        if 16>timehour>9:

            hours_before = datetime.datetime.strptime(datetime.datetime.now().strftime('%Y-%m-%d') + ' 10:00:00','%Y-%m-%d %H:%M:%S')
            hours_jichu=datetime.datetime.strptime(datetime.datetime.now().strftime('%Y-%m-%d') + ' 10:02:00','%Y-%m-%d %H:%M:%S')
            hours_after = datetime.datetime.now()
            jichu_jirou = guo_pen(hours_before, hours_jichu)

            hours_before_jiangbo = datetime.datetime.strptime(datetime.datetime.now().strftime('%Y-%m-%d') + ' 2:00:00','%Y-%m-%d %H:%M:%S')

            hours_after_jiangbo=datetime.datetime.now()+datetime.timedelta(hours=-8)

            jirou_weight = get_dingdan_jirou(hours_before_jiangbo,hours_after_jiangbo)

            yaji_guo = yaji_done(hours_before,hours_after)

            jirou_remain = (jichu_jirou + yaji_guo) * 6.8 - jirou_weight

            if len(li_jirou_gf)==0:
                li_jirou_gf.append(40)
                color_jirou_gf.append('red')
            if (datetime.datetime.now() - jirou_gf_time).seconds > 30:

                if 20 >jirou_remain > 0:
                    color_jirou_gf.append('green')
                elif 40>jirou_remain > 20:
                    color_jirou_gf.append('blue')
                elif jirou_remain>40:
                    color_jirou_gf.append('red')
                elif jirou_remain<0:
                    color_jirou_gf.append('magenta')

                li_jirou_gf.append(jirou_remain)
                jirou_gf_time = datetime.datetime.now()
                ax.clear()
                ax.set_title('压好的鸡肉', fontsize=30, color="black")
                ax.bar(range(len(li_jirou_gf)), li_jirou_gf, width=0.4, color=color_jirou_gf)
                plt.pause(5)
                if len(li_jirou_gf)>10:
                    del li_jirou_gf[1]
                if len(color_jirou_gf)>10:
                    del color_jirou_gf[1]

        else:
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_facecolor('#A9A9A9')
            plt.pause(5)



