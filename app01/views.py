from django.shortcuts import render, HttpResponse, redirect
from app01 import models
from django.forms import ModelChoiceField, ModelMultipleChoiceField


# from django.forms import Form
# from django.forms import fields
# from django.forms import widgets
#
# class TestForm(Form):
#     user = fields.CharField()
#     # group = ModelChoiceField(queryset=models.UserInfo.objects.all())  # 单选
#     group = ModelMultipleChoiceField(queryset=models.UserGroup.objects.all()) # 多选
#
# def test(request):
#     form = TestForm()
#     return render(request, 'test.html', {'form': form})
#



def test(request):
    """
    popup测试
    :param request:
    :return:
    """
    user_group_list = models.UserGroup.objects.all()
    return render(request, 'test.html', {'user_group_list': user_group_list})


def add_test(request):
    """
    popup添加测试
    :param request:
    :return:
    """
    if request.method == "GET":
        return render(request, 'add_test.html')
    else:
        # popup的操作中添加了ID，ug_ID
        popid = request.GET.get('popup')  # 获取URL中的ID，每个select的ID
        if popid:
            # 通过popip新建一个页面
            title = request.POST.get('title')
            obj = models.UserGroup.objects.create(title=title)
            # 增加完数据后要 1 关闭popup页面 2 把数据添加到标签中
            # 以上两个功能通过response.html进行操作
            return render(request, 'popup_response.html', {'id': obj.id, 'title': obj.title, 'popid': popid})
            # 把obj.id obj.title 是新添加的数据的id和内容，popid是select标签的ID，这里是ug_ID
            # 把这三个数据发送到前端
        else:
            # 不是通过popup的访问，
            title = request.POST.get('title')
            obj = models.UserGroup.objects.create(title=title)
            return HttpResponse('重定向页面')
