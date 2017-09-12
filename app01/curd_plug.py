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

    def edit_func(self, obj=None, is_header=False):
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
        if is_header:
            return "操作"
        else:
            # name = "{0}:{1}_{2}_change".format(self.site.namespace, self.model_class._meta.app_label,
            #                                    self.model_class._meta.model_name)
            # url = reverse(name, args=(obj.pk,))  # args 代表的是修改时的url中的参数 元组数据，这里必须是可迭代的对象
            from django.http.request import QueryDict
            param_dict = QueryDict(mutable=True)  # 创建对象并允许修改
            if self.request.GET:
                """
                request中有url中的请求信息，自己没有从父类中找，父类中的是self.request
                """
                param_dict['_changelistfilter'] = self.request.GET.urlencode()
            base_add_url = reverse('{0}:{1}_{2}_change'.format(self.site.namespace, self.app_label, self.model_name),
                                   args=(obj.pk,))  # args后面是元组数据
            edit_url = "{0}?{1}".format(base_add_url, param_dict.urlencode())  # param_dict继续urlencode把链接中的QueryDict去除

            return mark_safe("<a href='{0}'>编辑</a>".format(edit_url))

    def check_box(self, obj=None, is_header=False):
        if is_header:
            return "选项"
        else:
            tag = "<input value={} type='checkbox' name='pk'>".format(obj.pk)  # checkbox的value属性设置成pk 后台通过name属性获取
            return mark_safe(tag)

    def delete(self, obj=None, is_header=False):
        from django.urls import reverse
        if is_header:
            return "删除"
        else:
            from django.http.request import QueryDict
            param_dict = QueryDict(mutable=True)  # 创建对象并允许修改
            if self.request.GET:
                """
                request中有url中的请求信息，自己没有从父类中找，父类中的是self.request
                """
                param_dict['_changelistfilter'] = self.request.GET.urlencode()
            base_add_url = reverse('{0}:{1}_{2}_delete'.format(self.site.namespace, self.app_label, self.model_name),
                                   args=(obj.pk,))  # args后面是元组数据
            delete_url = "{0}?{1}".format(base_add_url, param_dict.urlencode())  # param_dict继续urlencode把链接中的QueryDict去除

            return mark_safe("<a href='{0}'>删除</a>".format(delete_url))

    def comb(self, obj=None, is_header=False):
        """
        在页面自定义列，通过函数名传递到前端

        :param obj:
        :param is_header:
        :return:
        """
        if is_header:
            return "自定义列"
        else:
            return "%s-%s" % (obj.username, obj.email)

    list_display = [check_box, 'id', 'username', 'email', comb, edit_func, delete]

    # ################################### 定制action操作 ###################################
    def initial(self, request):
        """
        定制action初始化操作
        :param request:
        :return: True 返回true的时候保存原来的条件
                False 返回列表页面
        """
        pk_list = request.POST.getlist('pk')  # 获取批量的id pk，pk是在设置的
        models.UserInfo.objects.filter(pk__in=pk_list).update(username="xxxxxx")
        return True

    initial.text = "初始化"  # 把函数名的text设置成中文

    def multi_del(self, request):
        """
        定制批量删除
        :param request:
        :return:
        """
        pass

    multi_del.text = "批量删除"

    action_list = [initial, multi_del]  # 定制的action操作列表

    # ########################################## 筛选条件 ##########################################

    from .filter_code import FilterOption
    """
    把对象封装到FilterOption类中，传入的参数：
    field_or_func：数据库的字段或者函数
    is_multi=False：是否是多选，这里默认是单选
    """
    filter_list = [
        FilterOption('username', False),
        FilterOption('ug', False),
        FilterOption('mmm', False),
    ]
    """
    # 1.取数据，放在页面上？
    #  username -> UserInfo表取数据
    #  ug       -> UserGroup表
    #  mmm      -> Role表
    # 2.单选和多选自定义
    # reuqest.GET    {'fk': [6,],'username': ['哈哈']} 数据结构是类似字典的结构，value的值是列表数据
    # reuqest.GET.urlencode() 通过urlencode把URL中的参数转换成fk=6&username=哈哈
    # 注意注意注意：
    # 保留当前URL条件 + 自身条件
    # - 单选： /arya/app01/userinfo/?mm=2&fk=2&username=哈哈
    # - 多选： /arya/app01/userinfo/?mm=2&fk=2&fk=7&username=哈哈
    # 反向生成url：reverse + reuqest.GET.urlencode()
    """


v1.site.register(models.UserInfo, CurdUserInfo)  # 把CurdUserInfo传入进去 xxx=BaseCurdAdmin进行接收


# v1.site.register(models.UserInfo)  # 默认__all__ 没有定制


class CurdRole(v1.BaseCurdAdmin):
    list_display = ['id', 'name']


v1.site.register(models.Role, CurdRole)  # 把CurdRole传进去 就是把list_display传进去

v1.site.register(models.UserGroup)  # 注册UserGroup
