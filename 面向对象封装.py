"""
面向对象封装的特点是：职责划分，封装什么就处理什么，然后给其他的类使用
FilterOption类中封装的是具体的处理功能，FilterList类中传入参数option，和data_list,
option:实例化对象的时候，传入的参数是FilterOption实例化的对象,就是FilterList可以调用FilterOption的属性和方法
data_list：用于__iter__ 的yield使用，yield后面是可迭代对象。
如果data_list 中的数据是数字类型，在操作的时候需要转换成字符串
"""


class FilterList(object):
    def __init__(self, option, data_list):
        self.option = option
        self.data_list = data_list

    @property
    def show(self):
        ret = self.option.nick  # 调用FilterOption中的nick方法
        return ret

    def __iter__(self):
        yield "全部"
        for i in self.data_list:
            # yield self.option.bs + str(i)
            yield "<a href='{0}'>{1}</a>".format(i, self.option.bs + str(i))


class FilterOption(object):
    def __init__(self, name, age):
        self.name = name
        self.age = age

    @property
    def nick(self):
        tpl = self.name + str(self.age)
        return tpl

    @property
    def bs(self):
        if self.age > 15:
            return "大"
        else:
            return "小"


obj_list = [
    FilterList(FilterOption('aaa', 9), [1, 2, 3]),
    FilterList(FilterOption('bbb', 19), [4, 5, 6]),
    FilterList(FilterOption('ccc', 9), [7, 8, 9]),
    FilterList(FilterOption('ddd', 18), [3, 5, 6])
]

for obj in obj_list:
    print(obj.show) # 调用show方法
    for item in obj:
        """
        对象中有__iter__和yield方法，还可以进行for循环
        """
        print(item, end='  ')
    else:
        print("")
