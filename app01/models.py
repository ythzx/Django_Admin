from django.db import models


class Role(models.Model):
    name = models.CharField(max_length=32)


class UserInfo(models.Model):
    username = models.CharField(max_length=32)
    email = models.EmailField(max_length=32)
