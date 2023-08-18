import re
from django.utils import timezone

from django.db import models
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import URLValidator
from django_mysql.models import JSONField

#app_bot
class Bot(models.Model):
    icon = models.CharField(max_length=255, null=False,verbose_name="图标")
    name = models.CharField(max_length=20, null=False, blank=False, unique=True,verbose_name="名字")
    introduction = models.TextField(max_length=255, null=True, blank=True,verbose_name="简介")
    created_User = models.CharField(max_length=255, null=False,verbose_name="创建人员")
    created_Date = models.DateTimeField(default=timezone.now,verbose_name="创建时间")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '机器人'

#判断当前输入是否为英文
def validate_english(value):
    if not re.match(r'^[a-zA-Z]*$', value):
        raise ValidationError(
            _('contain only English characters'),
            code='invalid_english'
        )

#意图
class Intent(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE,verbose_name="bot引用")
    name = models.CharField(max_length=20,null=False,blank=False,validators=[validate_english],verbose_name="意图名字")
    example = JSONField(default=list, help_text="列表格式",null=True,verbose_name="样例")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '意图'


#校验为英文，以“utter_"开头
def validate_utter_field(value):
    if not re.match(r'^utter_[a-zA-Z]+$', value):
        raise ValidationError('Field must start with "utter_" and contain only English characters.')


#响应
class Utterance(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE,verbose_name="bot引用")
    name = models.CharField(max_length=20,null=False,blank=False,validators=[validate_utter_field],verbose_name="响应名字")
    example = JSONField(default=list, help_text="列表格式",null=True,verbose_name="样例")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '响应'


#故事
class Story(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE,verbose_name="bot引用")
    icon = models.CharField(max_length=255, null=False,verbose_name="图标")
    name = models.CharField(max_length=50, null=False, blank=False,unique=True,verbose_name="故事名字")
    story_type = models.CharField(max_length=50,verbose_name="类型")
    example = JSONField(default=list, help_text="列表格式",null=True,verbose_name="样例")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '故事'



