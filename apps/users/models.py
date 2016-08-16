# ~*~ coding: utf-8 ~*~

from __future__ import unicode_literals

import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser, Permission
from django.contrib.auth.models import Group as AbstractGroup


class Role(AbstractGroup):
    comment = models.CharField(max_length=80, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'role'

    @classmethod
    def init(cls):
        roles = {
            'Administrator': {'permissions': Permission.objects.all(), 'comment': '管理员'},
            'User': {'permissions': [], 'comment': '用户'},
            'Auditor': {'permissions': Permission.objects.filter(content_type__app_label='audits'),
                        'comment': '审计员'},
        }

        for role in cls.objects.all():
            role.permissions.clear()

        cls.objects.all().delete()

        for role_name, props in roles.items():
            role = cls.objects.create(name=role_name, comment=props.get('comment', ''))
            role.permissions = props.get('permissions', [])


class UserGroup(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='组名称')
    comment = models.TextField(blank=True, verbose_name='描述')
    date_added = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'usergroup'

    @classmethod
    def init(cls):
        if not cls.objects.all():
            group = cls(name='所有人', comment='所有人默认都在用户组', created_by='System')
            group.save()


class User(AbstractUser):
    username = models.CharField(max_length=20, unique=True, verbose_name='用户名', help_text='* required')
    name = models.CharField(max_length=20, verbose_name='姓名', help_text='* required')
    email = models.EmailField(max_length=30, unique=True, verbose_name='邮件', help_text='* required')
    groups = models.ManyToManyField(UserGroup, verbose_name='用户组')
    avatar = models.ImageField(upload_to="avatar", verbose_name='头像', blank=True)
    wechat = models.CharField(max_length=30, blank=True, verbose_name='微信')
    phone = models.CharField(max_length=20, blank=True, verbose_name='手机号')
    enable_2FA = models.BooleanField(default=False, verbose_name='启用二次验证')
    secret_key_2FA = models.CharField(max_length=16, blank=True)
    role = models.ForeignKey(Role, on_delete=models.PROTECT, verbose_name='角色')
    private_key = models.CharField(max_length=5000, blank=True, verbose_name='ssh私钥')  # ssh key max length 4096 bit
    public_key = models.CharField(max_length=1000, blank=True, verbose_name='公钥')
    comment = models.TextField(max_length=200, blank=True, verbose_name='描述')
    created_by = models.CharField(max_length=30, default='')
    date_expired = models.DateTimeField(default=datetime.datetime.max, verbose_name='有效期')

    class Meta:
        db_table = 'user'
