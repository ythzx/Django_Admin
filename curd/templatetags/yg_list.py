from django.template import Library
from types import FunctionType

register = Library()

"""
前端不能通过getattr 这里通过yield  前端每循环一次，到yield这里取一次
row 代表每一行数据
"""

# def inner(result_list, list_display):
#     for row in result_list:
#         sub = []
#         for name in list_display:
#             val = getattr(row,name) # 循环取值
#             sub.append(val)
#         yield sub

"""
下面使用列表生成式和yield进行优化，只有在md.html循环的时候通过yield取这一次，提高效率
"""
def table_body(result_list, list_display,curd_obj):
    for row in result_list:
        # yield [getattr(row, name) for name in list_display]
        yield [name(curd_obj,row) if isinstance(name, FunctionType) else getattr(row, name) for name in list_display]
        """
        传递进来的参数中有定制的函数，通过FunctionType判断是否是函数，三元运算，是函数执行name() 传入参数row代表一行数据的的对象
        不是函数执行getattr获取数据
        name(curd_obj,row) 最终又把curd_obj 传回了curd_plug.py中的edit_func函数
        """

"""
前端调用模板函数
inclusion_tag 用于导入其他的HTML文件
返回值的结果给yd/md.html进行渲染，yd/md.html渲染完成后返回给前端
"""


def table_head(arg):
    pass


@register.inclusion_tag('yd/md.html')
def func(result_list, list_display,curd_obj):
    v = table_body(result_list, list_display,curd_obj)  # 通过inner函数生成相应的数据
    for item in list_display:
        if isinstance(item,FunctionType):
            print(item.__name__.title())
        else:
            print(item)
    return {'data': v}  # data 是[[],[],]列表套列表的数据类型
