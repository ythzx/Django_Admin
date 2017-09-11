from django.template import Library
from django.forms.models import ModelChoiceField
from django.urls import reverse
from curd.service import v1  # 导入模块中 应用单例模式 中的site
register = Library()


@register.inclusion_tag('yd/show_add_edit_form.html')  # 导入新的模板show_add_edit_form.html,数据在模板中渲染然
def show_add_edit_form(form):
    form_list = []
    for item in form:
        row = {'is_popup': False, 'item': None, 'popup_url': None}
        # if isinstance(item.field, ModelChoiceField) and item.field.queryset.model in v1.site._registry:
        if isinstance(item.field, ModelChoiceField) and item.field.queryset.model in v1.site._registry:
            """
            通过ModelChoiceField 判断是FK和M2M，ModelChoiceField和ModelMutipleChoiceField都是继承ChoiceField
            """
            target_app_label = item.field.queryset.model._meta.app_label
            target_model_name = item.field.queryset.model._meta.model_name
            url_name = "{0}:{1}_{2}_add".format(v1.site.namespace, target_app_label, target_model_name)
            target_url = reverse(url_name)

            row['is_popup'] = True
            row['item'] = item
            row['popup_url'] = target_url
        else:
            row['item'] = item
        form_list.append(row)
    return {'form_data': form_list}


# def form_data(form,curd_obj):
#     sub = []
#     for item in form:
#         val = []
#         ch_name = curd_obj.model_class._meta.get_field(item.name).verbose_name # 数据库中的中文字段名
#         val.append(ch_name)
#         val.append(item)
#         sub.append(val)
#     yield sub
#
#
# @register.inclusion_tag('yd/show_add_edit_form.html')
# def func(form,curd_obj):
#     v = form_data(form,curd_obj)
#     return {'data': v, }
