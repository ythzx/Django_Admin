from django.template import Library

register = Library()


def form_data(form,curd_obj):
    sub = []
    for item in form:
        val = []
        ch_name = curd_obj.model_class._meta.get_field(item.name).verbose_name # 数据库中的中文字段名
        val.append(ch_name)
        val.append(item)
        sub.append(val)
    yield sub


@register.inclusion_tag('yd/sh.html')
def func(form,curd_obj):
    v = form_data(form,curd_obj)
    return {'data': v, }
