from types import FunctionType


class FilterList(object):
    def __init__(self, option, queryset, request):
        self.option = option
        self.queryset = queryset
        self.request = request

    def __iter__(self):
        """
        有__iter__方法，才能被循环
        :return:
        """

        # 此时的row还可以封装option和request.GET
        for row in self.queryset:
            yield row # row代表每一个 queryset对象


class FilterOption(object):
    def __init__(self, field_or_func, is_multi=False, text_func_name=None, val_func_name=None):
        """
        :param field: 字段名称或函数
        :param is_multi: 是否支持多选
        :param text_func_name: 在Model中定义函数，显示文本名称，默认使用 str(对象)
        :param val_func_name:  在Model中定义函数，显示文本名称，默认使用 对象.pk
        """
        self.field_or_func = field_or_func
        self.is_multi = is_multi
        self.text_func_name = text_func_name
        self.val_func_name = val_func_name

    @property
    def is_func(self):
        if isinstance(self.field_or_func, FunctionType):
            return True

    @property
    def name(self):
        if self.is_func:
            return self.field_or_func.__name__
        else:
            return self.field_or_func
