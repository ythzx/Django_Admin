from django.shortcuts import render, HttpResponse, redirect
from django.urls import reverse


# 用于反向生成url


class BaseCurdAdmin(object):
    list_display = "__all__" # 用于展示所有的内容 这里是用于判断
    # list_display = [] # 也可以自己定制参数 这种情况不能进行定制 在注册的curd_plug.py中通过类写

    def __init__(self, model_class, site):
        self.model_class = model_class  # models_class 代表的是<class 'app01.models.Role'>
        self.site = site

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
        # print(self.model_class)
        # url = reverse('curd:app01_userinfo_changelist')  # 反向生成url
        # print(url)
        # return HttpResponse('...')
        result_list = self.model_class.objects.all()  # 通过model_class 就能获取数据库中的queryset数据
        print(result_list)
        print(self.list_display)  # 从注册类的curd_plug中传进来
        print(self.model_class)
        context = {
            'result_list': result_list,
            'list_display': self.list_display
        }
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
        data = '%s%s' % info
        return HttpResponse(data)


class CurdSite(object):
    def __init__(self):
        self._registry = {}
        self.namespace = 'curd'
        self.app_name = 'curd'

    def register(self, model_class, xxx=BaseCurdAdmin):
        self._registry[model_class] = xxx(model_class, self) # ？？？？？

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
