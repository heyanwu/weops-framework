from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Bot)
admin.site.register(models.Intent)
admin.site.register(models.Utterance)
admin.site.register(models.Story)