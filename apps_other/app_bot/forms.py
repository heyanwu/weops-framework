import json

from .models import Intent, Utterance, Story

from django import forms
class IntentForm(forms.ModelForm):
    class Meta:
        model = Intent
        fields = "__all__"
    example = forms.CharField(required=False)  # 将要修改的字段设置为非必填项
    example_1 = forms.CharField(required=False, label="Example 1")
    example_2 = forms.CharField(required=False, label="Example 2")
    example_3 = forms.CharField(required=False, label="Example 3")
    example_4 = forms.CharField(required=False, label="Example 4")
    example_5 = forms.CharField(required=False, label="Example 5")
    example_6 = forms.CharField(required=False, label="Example 6")
    example_7 = forms.CharField(required=False, label="Example 7")
    example_8 = forms.CharField(required=False, label="Example 8")
    example_9 = forms.CharField(required=False, label="Example 9")
    example_10 = forms.CharField(required=False, label="Example 10")

    def save(self, commit=True):
        instance = super().save(commit=False)

        # 将输入框中的数据合并成JSON列表
        example_list = []
        for i in range(1,11):
            data = self.cleaned_data[f'example_{i}']
            if data != '':
                example_list.append(data)


        # 将合并后的数据存储到example字段中
        instance.example = json.dumps(example_list)

        if commit:
            instance.save()

        return instance



class UtteranceForm(forms.ModelForm):
    class Meta:
        model = Utterance
        fields = "__all__"
    example = forms.CharField(required=False)  # 将要修改的字段设置为非必填项
    example_1 = forms.CharField(required=False, label="Example 1")
    example_2 = forms.CharField(required=False, label="Example 2")
    example_3 = forms.CharField(required=False, label="Example 3")
    example_4 = forms.CharField(required=False, label="Example 4")
    example_5 = forms.CharField(required=False, label="Example 5")
    example_6 = forms.CharField(required=False, label="Example 6")
    example_7 = forms.CharField(required=False, label="Example 7")
    example_8 = forms.CharField(required=False, label="Example 8")
    example_9 = forms.CharField(required=False, label="Example 9")
    example_10 = forms.CharField(required=False, label="Example 10")

    def save(self, commit=True):
        instance = super().save(commit=False)

        # 将输入框中的数据合并成JSON列表
        example_list = []
        for i in range(1,11):
            data = self.cleaned_data[f'example_{i}']
            if data != '':
                example_list.append(data)


        # 将合并后的数据存储到example字段中
        instance.example = json.dumps(example_list)

        if commit:
            instance.save()

        return instance

class StoryForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = "__all__"
    example = forms.CharField(required=False)  # 将要修改的字段设置为非必填项
    example_1 = forms.CharField(required=False, label="Example 1")
    example_2 = forms.CharField(required=False, label="Example 2")
    example_3 = forms.CharField(required=False, label="Example 3")
    example_4 = forms.CharField(required=False, label="Example 4")
    example_5 = forms.CharField(required=False, label="Example 5")
    example_6 = forms.CharField(required=False, label="Example 6")
    example_7 = forms.CharField(required=False, label="Example 7")
    example_8 = forms.CharField(required=False, label="Example 8")
    example_9 = forms.CharField(required=False, label="Example 9")
    example_10 = forms.CharField(required=False, label="Example 10")

    def save(self, commit=True):
        instance = super().save(commit=False)

        # 将输入框中的数据合并成JSON列表
        example_list = []
        for i in range(1,11):
            data = self.cleaned_data[f'example_{i}']
            if data != '':
                example_list.append(data)


        # 将合并后的数据存储到example字段中
        instance.example = json.dumps(example_list)

        if commit:
            instance.save()

        return instance