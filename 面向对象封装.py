class FilterList(object):
    def __init__(self, option, data_list):
        self.option = option
        self.data_list = data_list

    def show(self):
        self.option.nick()  # 调用FilterOption中的nick方法

    def __iter__(self):
        yield "全部"
        for i in self.data_list:
            yield self.option.bs + str(i)
            # yield "<a href='{0}'>{1}</a>".format(i, self.option.bs + i)


class FilterOption(object):
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def nick(self):
        tpl = self.name + str(self.name)
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
    for item in obj:
        print(item, end='  ')
    else:
        print("")
