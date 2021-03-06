from django.shortcuts import render, HttpResponse, redirect
from django.urls import reverse
import copy

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

    action_list = []  # 默认的action列表中为空，在注册页面进行操作

    filter_list = []  # 筛选条件

    add_or_edit_modelform = None

    def get_add_or_edit_modelform(self):
        if self.add_or_edit_modelform:
            return self.add_or_edit_modelform
        else:
            from django.forms import ModelForm
            # class MyModelForm(ModelForm):
            #     class Meta:
            #         model = self.model_class  # 代表了models中表名的类 动态
            #         fields = "__all__"

            # 通过type创建类
            _m = type('Meta', (object,), {'model': self.model_class, 'fields': "__all__"})
            MyModelForm = type('MyModelForm', (ModelForm,), {'Meta': _m})
            return MyModelForm

    def __init__(self, model_class, site):
        self.model_class = model_class  # models_class 代表的是<class 'app01.models.Role'>
        self.site = site
        self.request = None
        # 下面用于反向生成URL
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
        Django中request.GET获取的是QueryDict类型的数据，默认是不能修改的，通过参数mutable=True能进行修改
        :return:
        """
        # 生成页面上，添加按钮
        from django.http.request import QueryDict  # 通过type(request.GET)
        # print(request.GET,type(request.GET))
        param_dict = QueryDict(mutable=True)  # 创建对象并允许修改
        if request.GET:
            param_dict['_changelistfilter'] = request.GET.urlencode()  # 有encode方法 把对象中的数据转换成 page=1&name=2&
        # print(param_dict)
        base_add_url = reverse(
            '{0}:{1}_{2}_add'.format(self.site.namespace, self.app_label, self.model_name))  # namespace 在site中
        add_url = "{0}?{1}".format(base_add_url, param_dict.urlencode())  # param_dict继续urlencode把链接中的QueryDict去除

        # print(self.model_class)
        # url = reverse('curd:app01_userinfo_changelist')  # 反向生成url
        # print(url)
        # return HttpResponse('...')
        self.request = request  # 把request封装进来 包含请求信息

        # #################################### 分页 ####################################

        condition = {}  # 分页涉及筛选条件，把筛选的数据保存在condition 然后传入filter 中
        from curd.utils.pager import PageInfo
        current_page = request.GET.get('page')  # 从url中获取当前页
        all_count = self.model_class.objects.filter(**condition).count()  # 总的数据是筛选后的数据
        base_url = reverse('{0}:{1}_{2}_changelist'.format(self.site.namespace, self.app_label, self.model_name))  # 当前url
        # 保留url中的数据功能
        page_param_dict = copy.deepcopy(request.GET) # 通过深拷贝把URL中的数据复制一份,避免修改原来的数据
        page_param_dict._mutable = True # 设置成True就能修改QueryDict数据

        page_obj = PageInfo(current_page, all_count, 10, base_url,page_param_dict) # 把page_param_dict传递到分页中
        result_list = self.model_class.objects.filter(**condition)[page_obj.start:page_obj.end]
        # 通过model_class 就能获取数据库中的queryset数据



        # #################################### Action操作 ####################################
        # get请求,显示下拉框
        action_list = []
        for item in self.action_list:
            tpl = {'name': item.__name__, 'text': item.text}  # item.__name__ 是获取函数名,item.text获取设置的函数中文名
            action_list.append(tpl)
        if request.method == "POST":
            # 获取action
            func_name_str = request.POST.get('action')  # 获取select标签中选中的内容
            ret = getattr(self, func_name_str)(request)  # 通过字符串执行函数，并传入参数request，返回值是ret
            action_page_url = reverse(
                '{0}:{1}_{2}_changelist'.format(self.site.namespace, self.app_label, self.model_name)
            )
            if ret:
                # 返回值是true的时候
                action_page_url = "{0}?{1}".format(action_page_url, request.GET.urlencode())
            return redirect(action_page_url)

        # ################################ 组合搜索条件 ################################
        """
        把datalist(queryset数据)，封装到utils/fliter_code中的类中，同时把request封装进去（request.GET中的url信息）
        """
        from curd.utils.filter_code import FilterList
        filter_list = []
        for option in self.filter_list:
            """
            option代表的是注册的时候curd_plug.py中封装的对象
            filter_list = [
                FilterOption('username', False),
                FilterOption('ug', False),
                FilterOption('mmm', False),
            ]
            FilterList中有__iter__方法，才能被for循环
            """
            if option.is_func:
                """
                当是函数的时候,加括号执行函数，在这里向函数中传入参数self+request
                """
                data_list = option.field_or_func(self, request)  # 函数的返回值
            else:
                from django.db.models import ForeignKey, ManyToManyField
                field = self.model_class._meta.get_field(option.field_or_func)
                """
                option.field_or_func 此时是字符串类型，如何通过字符串判断是FK M2M？
                self.model_class找到类名，self.modle_class._meta.get_field('ug')加字符串找到相应的字段
                通过isinstance判断是否是FK M2M
                """
                if isinstance(field, ForeignKey):
                    """
                    通过FK字段找关联的表，ForeignKey中的to 传递给rel,rel中有model方法
                    field.rel.model就找到了FK关联的表，然后进行model查询数据
                    """
                    # print(field.rel.model) # UserGroup表
                    data_list = FilterList(option, field.rel.model.objects.all(), request.GET)  # 把对象,queryset,URL信息封装
                elif isinstance(field, ManyToManyField):
                    """
                    ManyToManyField 继承FK ，同上
                    """
                    # print(field.rel.model) # Role表
                    data_list = FilterList(option, field.rel.model.objects.all(), request.GET)
                else:
                    """
                    UserInfo 表中的CharField,通过field.model和self.model_class都能找到相应的表
                    """
                    # print(field.model,self.model_class) # UserInfo 表
                    data_list = FilterList(option, field.model.objects.all(), request.GET)
            filter_list.append(data_list)
            """
            之前的filter_list数据是三条Queryset数据，代表从数据库查询到的数据
            每一个Queryset还能循环，循环后的数据就是每一个对象
            最终filter_list中封装了option对象，queryset，request.GET
            """
        context = {
            'result_list': result_list,
            'list_display': self.list_display,
            'curd_obj': self,
            'add_url': add_url,
            'filter_list': filter_list,
            'action_list': action_list,
            'page_str':page_obj.pager
        }
        # 分页是把page_obj 的pager方法进行调用生成HTML
        # 注意把self这个对象传递到了前端
        return render(request, 'yd/change_list.html', context)

    def add_view(self, request):
        """
        增加数据
        :return:
        """
        # print(request.GET.get('_changelistfilter'))  # 获取url中的信息，最后进行拼接
        if request.method == "GET":
            modelform_obj = self.get_add_or_edit_modelform()()  # 先执行函数并实例化对象
        else:
            modelform_obj = self.get_add_or_edit_modelform()(data=request.POST, files=request.FILES)
            if modelform_obj.is_valid():
                obj = modelform_obj.save()  # save 的返回值是添加的数据
                popid = request.GET.get('popup')
                # 如果是通过popup提交的请求
                if popid:
                    pk = obj.pk  # pk是对象的id
                    title = str(obj)  # 通过__str__ 显示对象的中文
                    # 把数据封装到字典中data_dict 传到前端需要safe,否则Django内部会转义
                    return render(request, 'yd/popup_response.html',
                                  {'data_dict': {'pk': pk, 'title': title, 'popid': popid}})
                else:
                    # 提交成功后返回列表页面
                    base_list_url = reverse(
                        '{0}:{1}_{2}_changelist'.format(self.site.namespace, self.app_label,
                                                        self.model_name))  # namespace 在site中
                    list_url = "{0}?{1}".format(base_list_url, request.GET.get('_changelistfilter'))
                    return redirect(list_url)  # 跳转到新的列表页面
        context = {
            'form': modelform_obj,
            'curd_obj': self,
        }
        '''
        # 后台测试
        from django.forms.boundfield import BoundField
        from django.forms.models import ModelChoiceField,ModelMultipleChoiceField
        for item in modelform_obj:
            # print(self.model_class._meta.get_field(item.name).verbose_name) # 数据库中的中文字段名
            # print(item.name,item.field.label)  # item.field.label就是获取的数据库中的verbosename
            if isinstance(item.field,ModelChoiceField):
                # ModelMultipleChoiceField 继承 ModelChoiceField 所以FK和M2M中的都会打印
                print(item.field.queryset) # item.field.queryset ModelForm中实时刷新数据库用的是queryset
                # print(type(item.field.queryset))
                from django.db.models.query import QuerySet
                print(item.field.queryset.model) # <class 'app01.models.UserGroup'> model中有关联表
                print(item.field.queryset.model._meta.app_label) # 获取APP的名字
                print(item.field.queryset.model._meta.model_name) # 获取小写的表名
        '''
        return render(request, 'yd/add.html', context)

    def delete_view(self, request, pk):
        """
        删除数据
        1 通过pk获取数据
        2 删除数据
        :return:
        """
        if request.method == "GET":
            return render(request, 'yd/delete.html')
        else:
            obj = self.model_class.objects.filter(pk=pk).delete()
            base_list_url = reverse('{0}:{1}_{2}_changelist'.format(self.site.namespace, self.app_label,
                                                                    self.model_name))  # namespace 在site中
            list_url = "{0}?{1}".format(base_list_url, request.GET.get('_changelistfilter'))
            return redirect(list_url)  # 跳转到新的列表页面

    def change_view(self, request, pk):
        """
        修改数据
        1 从_changelistfilter中获取数据
        2 在页面显示默认值 instance
        :return:
        """
        obj = self.model_class.objects.filter(pk=pk).first()  # 从数据库中获取数据
        if not obj:
            return HttpResponse("id不存在")
        if request.method == "GET":
            modelform_obj = self.get_add_or_edit_modelform()(instance=obj)  # instance = obj 显示默认值
        else:
            modelform_obj = self.get_add_or_edit_modelform()(data=request.POST, files=request.FILES, instance=obj)
            # 参数中的instance代表修改数据，不加此参数，默认是增加数据
            if modelform_obj.is_valid():
                modelform_obj.save()
                base_list_url = reverse(
                    '{0}:{1}_{2}_changelist'.format(self.site.namespace, self.app_label,
                                                    self.model_name))  # namespace 在site中
                list_url = "{0}?{1}".format(base_list_url, request.GET.get('_changelistfilter'))
                return redirect(list_url)  # 跳转到新的列表页面
        context = {
            'form': modelform_obj
        }
        return render(request, 'yd/edit.html', context)


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
            ret.append(url(r'^%s/%s/' % (app_label, model_name), include(curd_admin_obj.urls)))
            # 生成url
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
