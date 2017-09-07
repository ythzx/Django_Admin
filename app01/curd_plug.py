from curd.service import v1
from app01 import models
from django.utils.safestring import mark_safe

"""
此文件的用处：在每个APP中把当前APP的表注册到CURD插件中，参考的Django的admin文件
同时，在这里进行了自定制操作，list_display中的内容最终显示在页面
"""


class CurdUserInfo(v1.BaseCurdAdmin):
    """
    list_display 中的是数据库中的字段
    把list_display 传入BaseCurdAdmin类中，在v1中直接用self.list_display使用
    list_display 进行自定制操作
    自定制把函数名传递进去，用于编辑修改等操作
    """

    def edit_func(self, obj):
        from django.urls import reverse
        """
        ！！self从yg_list.py接收过来 name(curd_obj,row) self中就有了model_class对象
        obj是yg_list中传入的参数row，代表一行数据
        obj.pk pk primary key 代表的就是 nid
        反向生成url需要app名字 类名 namespace
        反向生成url的格式是：'%s_%s_changelist'  -- namespace : %s_%s_changelist
        :return: 函数的返回值就是页面显示的数据
        """
        # print(type(obj)._meta.app_label) # 通过type() 把obj变成类的对象
        # print(type(obj)._meta.model_name)
        # print(v1.site.namespace) # v1实例化一次后就是固定的，单例模式，v1中有namespace

        # name = '{0}:{1}_{2}_change'.format(v1.site.namespace, type(obj)._meta.app_label, type(obj)._meta.model_name)
        name = "{0}:{1}_{2}_change".format(self.site.namespace, self.model_class._meta.app_label,
                                           self.model_class._meta.model_name)
        url = reverse(name, args=(obj.pk,))  # args 代表的是修改时的url中的参数 元组数据，这里必须是可迭代的对象
        print(url)
        return mark_safe("<a href='{0}'>编辑</a>".format(url))

    def check_box(self, obj):
        tag = "<input type='checkbox' value='{}'>".format(obj.pk)
        return mark_safe(tag)

    list_display = [check_box, 'id', 'username', 'email', edit_func]


v1.site.register(models.UserInfo, CurdUserInfo)  # 把CurdUserInfo传入进去 xxx=BaseCurdAdmin进行接收


class CurdRole(v1.BaseCurdAdmin):
    list_display = ['id', 'name']


v1.site.register(models.Role, CurdRole)  # 把CurdRole传进去 就是把list_display传进去
