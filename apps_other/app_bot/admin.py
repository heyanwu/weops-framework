import json

from django.contrib import admin
from django.utils.safestring import mark_safe

from . import models

from django.contrib import admin
from .models import Intent, Utterance, Story, Slot, FormInfo, FormSlotInfo
from .forms import IntentForm, UtteranceForm, StoryForm
from django import forms
#注册bot
admin.site.register(models.Bot)

#注册intent
class IntentAdminForm(forms.ModelForm):
    class Meta:
        model = Intent
        fields = '__all__'

    def clean_example(self):
        example = self.cleaned_data.get('example')
        try:
            # 尝试解析输入的 example 字段
            example_data = json.loads(example)
            if not isinstance(example_data, list) or len(example_data) < 2:
                raise forms.ValidationError("example 字段必须包含至少两个变量", "", 0)
        except json.JSONDecodeError:
            raise forms.ValidationError("example 字段必须是有效的 JSON 格式")
        return example

class IntentAdmin(admin.ModelAdmin):
    form = IntentAdminForm
admin.site.register(Intent,IntentAdmin)

#注册utterance
class UtteranceAdminForm(forms.ModelForm):
    class Meta:
        model = Utterance
        fields = '__all__'

    def clean_example(self):
        example = self.cleaned_data.get('example')
        try:
            # 尝试解析输入的 example 字段
            json.loads(example)
        except json.JSONDecodeError:
            raise forms.ValidationError("example 字段必须是有效的 JSON 格式")
        return example

class UtteranceAdmin(admin.ModelAdmin):
    form = UtteranceAdminForm
admin.site.register(Utterance,UtteranceAdmin)

#注册story
class StoryAdminForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = '__all__'

    def clean_example(self):
        example = self.cleaned_data.get('example')
        try:
            # 尝试解析输入的 example 字段
            json.loads(example)
        except json.JSONDecodeError:
            raise forms.ValidationError("example 字段必须是有效的 JSON 格式")
        return example

class StoryAdmin(admin.ModelAdmin):
    form = StoryAdminForm
admin.site.register(Story,StoryAdmin)

#槽
class SlotAdminForm(forms.ModelForm):
    class Meta:
        model = Slot
        fields = '__all__'

    def clean_slot_type(self):
        slot_type = self.cleaned_data['slot_type']
        try:
            json.loads(slot_type)
        except json.JSONDecodeError:
            raise forms.ValidationError("slot_type 必须是有效的 JSON 数据。")
        return slot_type

    def clean_mapping(self):
        mapping = self.cleaned_data['mapping']
        try:
            json.loads(mapping)
        except json.JSONDecodeError:
            raise forms.ValidationError("mapping 必须是有效的 JSON 数据。")
        return mapping
class SlotAdmin(admin.ModelAdmin):
    form = SlotAdminForm
admin.site.register(Slot,SlotAdmin)


admin.site.register(FormInfo)

class FormSlotAdminForm(forms.ModelForm):
    class Meta:
        model = FormSlotInfo
        fields = '__all__'

    def clean_question(self):
        question = self.cleaned_data['question']
        try:
            json.loads(question)
        except json.JSONDecodeError:
            raise forms.ValidationError("slot_type 必须是有效的 JSON 数据。")
        return question
class FormSlotAdmin(admin.ModelAdmin):

    form = SlotAdminForm

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

            #判断模式
            utter_ask_name = f"utter_ask_{obj.slot.name}"
            bot_id = obj.slot.bot_id
            question = obj.question
            utterance_ask, created = Utterance.objects.update_or_create(name=utter_ask_name,example=question,bot_id=bot_id)
            utterance_ask.save()

            utter_valid_name = f"utter_valid_{obj.slot.name}"
            utter_invalid_name = f"utter_invalid_{obj.slot.name}"
            valid = obj.valid_prompts
            invalid = obj.invalid_prompts
            utterance_valid, created = Utterance.objects.update_or_create(name=utter_valid_name, example=valid,
                                                                     bot_id=bot_id)
            utterance_valid.save()

            utterance_invalid, created = Utterance.objects.update_or_create(name=utter_invalid_name, example=invalid,
                                                                       bot_id=bot_id)
            utterance_invalid.save()


admin.site.register(FormSlotInfo,FormSlotAdmin)

