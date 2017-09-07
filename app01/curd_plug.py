from curd.service import v1
from app01 import models

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
    def edit_func(obj):
        """
        obj是yg_list中传入的参数row，代表一行数据
        :return: 函数的返回值就是页面显示的数据
        """
        return "编辑"
    list_display = ['id', 'username', 'email',edit_func]


v1.site.register(models.UserInfo, CurdUserInfo)  # 把CurdUserInfo传入进去 xxx=BaseCurdAdmin进行接收


class CurdRole(v1.BaseCurdAdmin):
    list_display = ['id', 'name']


v1.site.register(models.Role, CurdRole)  # 把CurdRole传进去 就是把list_display传进去
