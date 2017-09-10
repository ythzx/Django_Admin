from django.shortcuts import render, HttpResponse, redirect
from django.urls import reverse

"""
使用文档：
1. 数据列表页面,定制显示烈
    示例一：
        v1.site.register(models.UserInfo)， 默认只显示对象列表


    示例二：
        class CurdUserInfo(v1.BaseCurdAdmin):
            list_display = []

        v1.site.register(Model,SubClass), 按照list_display中指定的字段进行显示
        PS: 字段可以
                - 字符串，必须是数据库列明
                - 函数，
                    def comb(self,obj=None,is_header=False):
                        if is_header:
                            return "自定义列"
                        else:
                            return "%s-%s"%(obj.username,obj.email)

            完整示例如下：
                class CurdUserInfo(v1.BaseCurdAdmin):
                    def edit_func(self, obj=None,is_header=False):
                        from django.urls import reverse
                        # print(type(obj)._meta.app_label) # 通过type() 把obj变成类的对象
                        # print(type(obj)._meta.model_name)
                        # print(v1.site.namespace) # v1实例化一次后就是固定的，单例模式，v1中有namespace

                        # name = '{0}:{1}_{2}_change'.format(v1.site.namespace, type(obj)._meta.app_label, type(obj)._meta.model_name)
                        if is_header:
                            return "操作"
                        else:
                            name = "{0}:{1}_{2}_change".format(self.site.namespace, self.model_class._meta.app_label,
                                                               self.model_class._meta.model_name)
                            url = reverse(name, args=(obj.pk,))  # args 代表的是修改时的url中的参数 元组数据，这里必须是可迭代的对象
                            print(url)
                            return mark_safe("<a href='{0}'>编辑</a>".format(url))

                    def check_box(self,obj=None,is_header=False):
                        if is_header:
                            return "选项"
                        else:
                            tag = "<input type='checkbox' value='{}'>".format(obj.pk)
                            return mark_safe(tag)

                    def comb(self,obj=None,is_header=False):

                        if is_header:
                            return "自定义列"
                        else:
                            return "%s-%s"%(obj.username,obj.email)

                    list_display = [check_box, 'id', 'username', 'email',comb, edit_func]
"""


class BaseCurdAdmin(object):
    """
    处理所有的请求信息
    """
    list_display = "__all__"  # 用于展示所有的内容 这里是用于判断

    # list_display = [] # 也可以自己定制参数 这种情况不能进行定制 在注册的curd_plug.py中通过类写

    def __init__(self, model_class, site):
        self.model_class = model_class  # models_class 代表的是<class 'app01.models.Role'>
        self.site = site
        self.request = None

        self.app_label = model_class._meta.app_label
        self.model_name = model_class._meta.model_name

    @property
    def urls(self):
        from django.conf.urls import url, include
        info = self.model_class._meta.app_label, self.model_class._meta.model_name  # 自动生成元组如('app01', 'userinfo')
        # self.model_class._meta.app_label是app名字 和 elf.model_class._meta.model_name小写的表明

        """
        通过源码中admin的option中找到
        """
        urlpatterns = [
            url(r'^$', self.changelist_view, name='%s_%s_changelist' % info),  # 元组数据自动分开赋值
            url(r'^add/$', self.add_view, name='%s_%s_add' % info),
            url(r'^(.+)/delete/$', self.delete_view, name='%s_%s_delete' % info),
            url(r'^(.+)/change/$', self.change_view, name='%s_%s_change' % info),
        ]
        return urlpatterns

    def changelist_view(self, request):
        """
        查看列表，是指定默认页面的函数
        :return:
        """
        # 生成页面上，添加按钮
        from django.http.request import QueryDict
        param_dict = QueryDict(mutable=True)  # 创建对象并允许修改
        if request.GET:
            param_dict['_changelistfilter'] = request.GET.urlencode()  # 有encode方法 把对象中的数据转换成 page=1&name=2&
        print(param_dict)
        base_add_url = reverse(
            '{0}:{1}_{2}_add'.format(self.site.namespace, self.app_label, self.model_name))  # namespace 在site中
        add_url = "{0}?{1}".format(base_add_url, param_dict.urlencode())  # param_dict继续urlencode把链接中的QueryDict去除

        # print(self.model_class)
        # url = reverse('curd:app01_userinfo_changelist')  # 反向生成url
        # print(url)
        # return HttpResponse('...')
        self.request = request  # 把request封装进来 包含请求信息
        result_list = self.model_class.objects.all()  # 通过model_class 就能获取数据库中的queryset数据
        # print(result_list)
        # print(self.list_display)  # 从注册类的curd_plug中传进来
        # print(self.model_class)
        context = {
            'result_list': result_list,
            'list_display': self.list_display,
            'curd_obj': self,
            'add_url': add_url
        }
        # 注意把self这个对象传递到了前端
        return render(request, 'yd/change_list.html', context)

    def add_view(self, request):
        """
        增加数据
        :return:
        """
        info = self.model_class._meta.app_label, self.model_class._meta.model_name  # 自动生成元组
        data = '%s%s' % info
        return HttpResponse(data)

    def delete_view(self, request, pk):
        """
        删除数据
        :return:
        """
        info = self.model_class._meta.app_label, self.model_class._meta.model_name  # 自动生成元组
        data = '%s%s' % info
        return HttpResponse(data)

    def change_view(self, request, pk):
        """
        修改数据
        :return:
        """

        info = self.model_class._meta.app_label, self.model_class._meta.model_name  # 自动生成元组
        data = '%s%s编辑页面' % info
        return HttpResponse(data)


class CurdSite(object):
    """
    程序入口类 用于注册models
    """

    def __init__(self):
        self._registry = {}
        self.namespace = 'curd'  # 反向生成URL
        self.app_name = 'curd'

    def register(self, model_class, xxx=BaseCurdAdmin):
        self._registry[model_class] = xxx(model_class, self)  # ？？？？？

    def get_urls(self):
        from django.conf.urls import url, include
        ret = [

        ]
        for model_cls, curd_admin_obj in self._registry.items():
            app_label = model_cls._meta.app_label
            model_name = model_cls._meta.model_name

            # ret.append(url(r'^%s/%s' % (app_label, model_name), self.login))
            ret.append(url(r'^%s/%s' % (app_label, model_name), include(curd_admin_obj.urls)))
            # include中的参数 第一个是curd_admin_obj对象 urls是 BaseCurdAdmin的对象
        return ret

    @property
    def urls(self):
        return self.get_urls(), self.app_name, self.namespace

    def login(self, request):
        return HttpResponse('login')

    def logout(self, request):
        return HttpResponse('logout')


site = CurdSite()  # 实例化对象，就是self 这里就是单例模式
