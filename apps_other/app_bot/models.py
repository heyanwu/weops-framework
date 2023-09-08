# _*_ coding:utf-8 _*_

import re

from django.db.models import UniqueConstraint
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from django.db import models
import re
from django.core.exceptions import ValidationError
from django.utils.html import escape
from django.utils.translation import gettext_lazy as _
from django.core.validators import URLValidator
from django_mysql.models import JSONField

#app_bot
class Bot(models.Model):
    icon = models.CharField(max_length=255, null=False,verbose_name="图标")
    name = models.CharField(max_length=20, null=False, blank=False, verbose_name="名字")
    introduction = models.TextField(max_length=255, null=True, blank=True,verbose_name="简介")
    created_User = models.CharField(max_length=255, null=False,verbose_name="创建人员")
    created_Date = models.DateTimeField(default=timezone.now,verbose_name="创建时间")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '机器人'
        verbose_name_plural = "机器人"
        constraints = [
            UniqueConstraint(fields=['name', 'created_User'], name='unique_name_per_user')
        ]

#判断当前输入是否为英文和特殊字符
def validate_english(value):
    if not re.match(r'^[a-zA-Z!@#$%^&*()_+\-=[\]{};:\'",.<>/?\\|]*$', value):
        raise ValidationError(
            _('Should contain only English characters or special characters'),
            code='invalid_english_or_special'
        )

#意图
class Intent(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE,verbose_name="bot引用")
    name = models.CharField(max_length=20,null=False,blank=False,validators=[validate_english],verbose_name="意图名字")
    example = models.TextField(max_length=1024,default=list, help_text="列表格式",null=True,verbose_name="样例")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '意图'
        verbose_name_plural = "意图"
        constraints = [
            UniqueConstraint(fields=['name', 'bot'], name='unique_name_per_bot')
        ]


#校验为英文，以“utter_"开头
def validate_utter_field(value):
    if not re.match(r'^utter_[a-zA-Z!@#$%^&*()_+\-=[\]{};:\'",.<>/?\\|]+$', value):
        raise ValidationError('Field must start with "utter_" and contain only English characters.')


#响应
class Utterance(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE,verbose_name="bot引用")
    name = models.CharField(max_length=50,null=False,blank=False,validators=[validate_utter_field],verbose_name="响应名字")
    example = models.TextField(default=list, help_text="列表格式",null=True,verbose_name="样例")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '响应'
        verbose_name_plural = "响应"
        constraints = [
            UniqueConstraint(fields=['name', 'bot'], name='unique_name_per_bot')
        ]


#故事
class Story(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE,verbose_name="bot引用")
    icon = models.CharField(max_length=255, null=False,verbose_name="图标")
    name = models.CharField(max_length=255, null=False, blank=False,verbose_name="故事名字")
    story_type = models.CharField(max_length=50,verbose_name="类型")
    example = models.TextField(max_length=1024,default=list, help_text="列表格式",null=True,verbose_name="样例")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '故事'
        verbose_name_plural = "故事"
        constraints = [
            UniqueConstraint(fields=['name', 'bot'], name='unique_name_per_bot')
        ]

#槽
class Slot(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE, verbose_name="bot引用")
    name = models.CharField(max_length=50, null=False, blank=False,verbose_name="槽名",validators=[validate_english])
    slot_type = models.TextField(default=dict,blank=True,help_text="槽类型信息，请填写槽的具体信息",verbose_name="槽类型")
    influence = models.BooleanField(default=True,verbose_name="影响对话")
    mapping = models.TextField(default=list,blank=True,help_text="槽映射信息，请填写槽的具体信息",verbose_name="槽映射")
    initial_value = models.CharField(max_length=20,null=True,blank=True,verbose_name="初始值")
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '槽'
        verbose_name_plural = "槽"
        constraints = [
            UniqueConstraint(fields=['name', 'bot'], name='unique_name_per_bot')
        ]

#表单
class FormInfo(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE, verbose_name="bot引用")
    slots = models.ManyToManyField(Slot)
    name = models.CharField(max_length=50, null=False, blank=False,verbose_name="表单名")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '表单'
        verbose_name_plural = "表单"
        constraints = [
            UniqueConstraint(fields=['name', 'bot'], name='unique_name_per_bot')
        ]

#表单中槽详细信息
class FormSlotInfo(models.Model):
    forminfo = models.ForeignKey(FormInfo, on_delete=models.CASCADE, verbose_name="表单引用")
    slot = models.ForeignKey(Slot,on_delete=models.CASCADE,verbose_name="槽")
    validation = models.TextField(default=list, blank=True, help_text="请输入该槽验证的值，即支持的范围，以“,”分隔",
                           verbose_name="验证值")
    question = models.TextField(default=list,blank=True,help_text="bot回复的提示",verbose_name="询问列表")
    valid_prompts = models.CharField(max_length=200, null=True, blank=True,verbose_name="有效提示")
    invalid_prompts = models.CharField(max_length=200, null=True, blank=True,verbose_name="无效提示")
    class Meta:
        verbose_name = '表单中槽详细信息'
        verbose_name_plural = "表单中槽详细信息"

# 添加信号处理函数
@receiver(post_save, sender=FormSlotInfo)
def update_related_m2m(sender, instance, **kwargs):
    instance.forminfo.slots.add(instance.slot)
    instance.slot.forminfo_set.add(instance.forminfo)