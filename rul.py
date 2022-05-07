path('admin/', admin.site.urls),
path('DD/OrderStatus/', views.dd_deliver),
path('ceshi/', views.ceshi),
re_path('^SF/Callback/$', views.sf_callback),


\
from django.shortcuts import render
from django.http import HttpResponse
import os
# Create your views here.

def wei_jie(request):
    return HttpResponse('OK')


def get_photo(request):
    """定义接收文件的视图"""
    # ----简单文件上传----
    if request.method == 'POST':

        if request.FILES:

            print('okkkkkk')
            imgs = request.FILES.getlist('files')

            print(imgs)
            dir = './pic_save/'
            if not os.path.exists(os.path.dirname(dir)):
                os.makedirs(os.path.dirname(dir))
            for f in imgs:
                print(f)
                with open(dir + str(f), 'wb') as dest:
                    for chunk in f.chunks():
                        dest.write(chunk)
    return HttpResponse('ok')




# -*- coding:utf-8 -*-
import datetime
from django.shortcuts import render
from django.http import HttpResponse
import json
import jsonpath
from dataport import mysql_tengxun
from django.http import JsonResponse
import time

def sf_callback(request):

    sf_status = request.GET.get('t', None)

    if sf_status == 'changed':

        content = json.loads(request.body)

        print(content)

        sf_order_id = jsonpath.jsonpath(content, '$..sf_order_id')[0]
        shop_order_id = jsonpath.jsonpath(content, '$..shop_order_id')[0]
        order_status = jsonpath.jsonpath(content, '$..order_status')[0]
        url_index = jsonpath.jsonpath(content, '$..url_index')[0]
        operator_name = jsonpath.jsonpath(content, '$..operator_name')[0]
        operator_phone = int(jsonpath.jsonpath(content, '$..operator_phone')[0])
        push_time = int(jsonpath.jsonpath(content, '$..push_time')[0])
        timeArray = time.localtime(push_time)
        push_time = datetime.datetime.strptime(time.strftime("%Y-%m-%d %H:%M:%S", timeArray), "%Y-%m-%d %H:%M:%S")

        sql = "insert into sf_callback set creat_time='%s',sf_order_id='%s',order_id='%s',order_status='%s',url_index='%s',operator_name='%s',operator_phone='%s',push_time='%s'" % (
            datetime.datetime.now(), sf_order_id, shop_order_id, order_status, url_index, operator_name, operator_phone,
            push_time)
        while 1:
            try:
                mysql_tengxun.mysql_db(sql)
                print('insert_one_data')
                break
            except:
                time.sleep(1)
                print('insert___date__error')
                continue

        return JsonResponse({
            "error_code": 0,
            "error_msg": "success"
        })

    if sf_status == 'arrived':

        content = json.loads(request.body)

        print(content)

        return JsonResponse({
            "error_code": 0,
            "error_msg": "success"
        })

    else:
        return JsonResponse({
            "error_code": 0,
            "error_msg": "success"
        })


def dd_deliver(request):

    content=json.loads(request.body)

    print(content)

    order_id = jsonpath.jsonpath(content, '$..order_id')[0]
    order_status = jsonpath.jsonpath(content, '$..order_status')[0]
    cancel_reason= jsonpath.jsonpath(content, '$..cancel_reason')[0]
    cancel_from= jsonpath.jsonpath(content, '$..cancel_from')[0]
    dm_id=int(jsonpath.jsonpath(content, '$..dm_id')[0])
    if dm_id!=0:
        dm_name= jsonpath.jsonpath(content, '$..dm_name')[0]
        dm_mobile= jsonpath.jsonpath(content, '$..dm_mobile')[0]
        update_time= int(jsonpath.jsonpath(content, '$..update_time')[0])
        timeArray = time.localtime(update_time)
        update_time = datetime.datetime.strptime(time.strftime("%Y-%m-%d %H:%M:%S", timeArray), "%Y-%m-%d %H:%M:%S")
        is_finish_code=jsonpath.jsonpath(content, '$..is_finish_code')[0]

        sql = "insert into dd_callback set creat_time='%s',order_id='%s',order_status='%s',cancel_reason='%s',cancel_from='%s',dm_id='%s',dm_name='%s',dm_mobile='%s',is_finish_code='%s',update_time='%s'" % (
            datetime.datetime.now(), order_id, order_status, cancel_reason, cancel_from, dm_id, dm_name, dm_mobile,is_finish_code,update_time)
        while 1:
            try:
                mysql_tengxun.mysql_db(sql)
                print('insert_one_data')
                break
            except:
                time.sleep(1)
                print('insert___date__error')
                continue

    return HttpResponse('ok')

def ceshi(request):

    return HttpResponse('ok')

def get_data(request):
    project_data = {}
    data_tem=ZaoyanTimelong.objects.values_list('zaoyan_num','timelong')
    for i in list(data_tem):
        project_data[i[0]]=i[1]
    return render(request, "get_zaoyan.html", {'project': project_data})


def update_psquhuo(request):

    orderid=request.GET.get('order_id')
    Order2.objects.filter(order_id=orderid).update(dingdan_status=2)
    update_peisong.main('王河', '13581964705', orderid, 20)
    return HttpResponse('取货成功，请尽快配送')

def update_psdone(request):

    orderid=request.GET.get('order_id')
    Order2.objects.filter(order_id=orderid).update(dingdan_status=3)
    update_peisong.main('王河', '13581964705', orderid, 40)
    return HttpResponse('配送完成订单，请到配送完成界面查询')

def update_ps(request):

    orderid=request.GET.get('order_id')
    dingdan=Order2.objects.filter(order_id=orderid)

    if dingdan[0].peisongy=='None':
        Order2.objects.filter(order_id=orderid).update(peisongy='王河',peisongy_phone='13581964705',dingdan_status=1)
        update_peisong.main('王河','13581964705',orderid,10)
        return HttpResponse('接单成功，请到已接单界面查看')

    else:
        return HttpResponse('订单已经被其他骑手接单，请刷新未接单！')

def ps_weijie(request):

    now_time=datetime.datetime.now()+datetime.timedelta(hours=-3)
    data=Order2.objects.filter(creat_time__gt=now_time,peisongy='None',platform='美团').exclude(dingdan_status=-4)

    for i in range(len(data)):

        if '_' in data[i].phonelist:

            data[i].tips=data[i].phonelist.split('_')[0]
            data[i].shipid='#'+str(data[i].phonelist.split('_')[1])+'#'
            data[i].phonelist=data[i].phonelist.split('_')[0]+','+data[i].phonelist.split('_')[1]

        else:
            data[i].phonelist = data[i].phonelist.replace('[','').replace(']','').replace('"','')

        data[i].latitude='http://uri.amap.com/navigation?from=116.457704,39.905014&&to='+str(data[i].longitude/1000000)+','+str(data[i].latitude/1000000)+'&mode=ride&src=nyx_super;'


    return render(request, 'ps_weijie.html', {"attack_method": data})

def ps_yijie(request):

    now_time=datetime.datetime.now()+datetime.timedelta(hours=-3)

    data=Order2.objects.filter(creat_time__gt=now_time,peisongy='王河',dingdan_status=1)

    for i in range(len(data)):
        if '_' in data[i].phonelist:
            data[i].tips=data[i].phonelist.split('_')[0]

            data[i].phonelist=data[i].phonelist.split('_')[0]+','+data[i].phonelist.split('_')[1]

        else:
            data[i].phonelist = data[i].phonelist.replace('[','').replace(']','').replace('"','')

        data[i].latitude='http://uri.amap.com/navigation?from=116.457704,39.905014&&to='+str(data[i].longitude/1000000)+','+str(data[i].latitude/1000000)+'&mode=ride&src=nyx_super;'


    return render(request, 'ps_yijie.html', {"attack_method": data})

def ps_quhuo(request):

    now_time=datetime.datetime.now()+datetime.timedelta(hours=-3)
    data=Order2.objects.filter(creat_time__gt=now_time,peisongy='王河',dingdan_status=2)

    for i in range(len(data)):

        if '_' in data[i].phonelist:

            data[i].tips=data[i].phonelist.split('_')[0]
            data[i].shipid='#'+str(data[i].phonelist.split('_')[1])+'#'
            data[i].phonelist=data[i].phonelist.split('_')[0]+','+data[i].phonelist.split('_')[1]

        else:
            data[i].phonelist = data[i].phonelist.replace('[','').replace(']','').replace('"','')

        data[i].latitude='http://uri.amap.com/navigation?from=116.457704,39.905014&&to='+str(data[i].longitude/1000000)+','+str(data[i].latitude/1000000)+'&mode=ride&src=nyx_super;'


    return render(request, 'ps_quhuo.html', {"attack_method": data})


def ps_done(request):

    now_time=datetime.datetime.now()+datetime.timedelta(hours=-3)
    data=Order2.objects.filter(creat_time__gt=now_time,peisongy='王河',dingdan_status=3)

    for i in range(len(data)):

        if '_' in data[i].phonelist:

            data[i].tips=data[i].phonelist.split('_')[0]
            data[i].shipid='#'+str(data[i].phonelist.split('_')[1])+'#'
            data[i].phonelist=data[i].phonelist.split('_')[0]+','+data[i].phonelist.split('_')[1]

        else:
            data[i].phonelist = data[i].phonelist.replace('[','').replace(']','').replace('"','')

        data[i].latitude='http://uri.amap.com/navigation?from=116.457704,39.905014&&to='+str(data[i].longitude/1000000)+','+str(data[i].latitude/1000000)+'&mode=ride&src=nyx_super;'


    return render(request, 'ps_done.html', {"attack_method": data})


