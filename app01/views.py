from django.shortcuts import render, HttpResponse, redirect
from app01 import models


def test(request):
    user_group_list = models.UserGroup.objects.all()
    return render(request, 'test.html', {'user_group_list': user_group_list})


def add_test(request):
    if request.method == "GET":
        return render(request,'add_test.html')
    else:
        popid = request.GET.get('popup')
        if popid:
            # 通过popip新建一个页面
            title = request.POST.get('title')
            obj = models.UserGroup.objects.create(title=title)
            return render(request,'popup_response.html',{'id':obj.id,'title':obj.title,'popid':popid})
        else:
            title = request.POST.get('title')
            obj = models.UserGroup.objects.create(title=title)
            return HttpResponse('重定向页面')




