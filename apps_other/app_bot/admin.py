from django.contrib import admin
from . import models

from django.contrib import admin
from .models import Intent, Utterance, Story, Slot, FormInfo, FormSlotInfo
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

admin.site.register(Slot)
admin.site.register(FormInfo)

class FormSlotAdmin(admin.ModelAdmin):
    list_display = ['get_slot_name', 'get_bot_id', 'question']

    def get_slot_name(self, obj):
        return obj.slot.name if obj.slot else None

    get_slot_name.short_description = 'Slot Name'

    def get_bot_id(self, obj):
        return obj.slot.bot_id if obj.slot else None

    get_bot_id.short_description = 'Bot ID'

    def save_model(self, request, obj, form, change):
        # 在保存FormSlotInfo数据时同时创建或更新Utterance数据
        super().save_model(request, obj, form, change)

        if obj.slot:  # 检查是否有关联的Slot
            utter_name = f"utter_ask_{obj.slot.name}"
            bot_id = obj.slot.bot_id
            utterance, created = Utterance.objects.get_or_create(name=utter_name,example=obj.question,bot_id=bot_id)
            utterance.save()

admin.site.register(FormSlotInfo,FormSlotAdmin)

