from django.apps import AppConfig


class CurdConfig(AppConfig):
    name = 'curd'

    def ready(self):
        """
        程序启动的时候先执行ready方法，执行autodiscover_modules，自定找APP中有curd_plug插件
        :return:
        """
        super(CurdConfig,self).ready()

        from django.utils.module_loading import autodiscover_modules
        autodiscover_modules('curd_plug')
