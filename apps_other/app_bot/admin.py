from django.contrib import admin
from . import models

from django.contrib import admin
from .models import Intent, Utterance, Story
from .forms import IntentForm, UtteranceForm, StoryForm

#注册bot
admin.site.register(models.Bot)

#注册intent
class IntentAdmin(admin.ModelAdmin):
    form = IntentForm
admin.site.register(Intent, IntentAdmin)

#注册utterance
class UtteranceAdmin(admin.ModelAdmin):
    form = UtteranceForm
admin.site.register(Utterance,UtteranceAdmin)

#注册story
class StoryAdmin(admin.ModelAdmin):
    form = StoryForm
admin.site.register(Story,StoryAdmin)
