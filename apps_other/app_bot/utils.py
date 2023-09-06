import os
import re

import yaml
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps_other.app_bot.models import Intent, Utterance, Story, Slot, FormSlotInfo


#目的是获取数据，解析成yaml数据
def nlu_yml(botId):
    # 生成YAML内容
    model_data = Intent.objects.all().filter(bot_id=botId).values("name", 'example')
    yaml_data = []
    for item in model_data:
        intent_data = {
            'intent': item['name'],
            'examples': item['example']
        }
        yaml_data.append(intent_data)

    return yaml_data

def response_yml(botId):

    model_data = dict(Utterance.objects.filter(bot_id=botId).values_list("name", 'example'))

    return model_data

def story_yml(botId):
    model_data = Story.objects.all().filter(bot_id=botId).values("story_type","name", 'example')
    story_data = []
    rule_data = []
    for item in model_data:
        if "story" in item['story_type']:
            data = {
                "story": item["name"],
                "steps":item["example"]
            }
            story_data.append(data)

        if "rule" in item['story_type']:
            data = {
                "rule": item["name"],
                "steps": item["example"]
            }
            rule_data.append(data)

    return story_data,rule_data

def domain_yml(botId):
    intents = Intent.objects.all().filter(bot_id=botId).values("name",'example')

    #意图列表
    intents_data = []

    #实体列表
    entities_data = []
    for item in intents:
        name = item["name"]
        intents_data.append(name)
        example = item["example"]
        pattern = r'\[.*?\]\((.*?)\)'
        for example_i in example:
            entity_matches = re.findall(pattern, example_i)
            if len(entity_matches) != 0:
                # 获取实体数量，都添加进来
                for entity in entity_matches:
                    entities_data.append(entity)

    slots = Slot.objects.all().filter(bot_id=botId)

    #槽列表
    slots_data = {}
    for slot in slots:
        name = slot.name

        #更换槽类型值
        slot_type_switcher = {
            "文本": "text",
            "布尔": "bool",
            "分类": "categorical",
            "数值": "float",
            "列表": "list",
            "任意": "any",

        }
        slot_type = slot.slot_type["type"]
        slot_type = slot_type_switcher[slot_type]
        slots_values = slot.slot_type
        slots_values.pop("type")
        influence_conversation = slot.influence
        initial_value = slot.initial_value

        #更换映射类型
        mapping_switcher = {
            "实体":"form_entity",
            "意图":"form_intent",
            "文本":"form_text",
        }
        mappings = slot.mapping
        for mapping in mappings:
            original_type = mapping["type"]
            mapping["type"] = mapping_switcher[original_type]

        slots_data[name] = {
            "type":slot_type,
            "values":slots_values,
            "influence_conversation":influence_conversation,
            "initial_value":initial_value,
            "mappings":mappings}

    #获取action，action存在故事里
    action_data = []
    stories = Story.objects.all().filter(bot_id=botId).values('example')
    for story in stories:
        example = story["example"]
        action = example["action"]
        action_data.append(action)

    #获取表单槽详细信息
    form_slots = FormSlotInfo.objects.all().filter(forminfo__bot_id=botId)
    form_slot_data = {}
    #首先获取forminfo
    for form_slot in form_slots:
        form_name = form_slot.forminfo.name
        if form_name not in form_slot_data:
            form_slot_data[form_name] = {
                'required_slots':[]
            }
        slot_name = form_slot.slot.name
        form_slot_data[form_name]['required_slots'].append(slot_name)

    return intents_data,entities_data,slots_data,action_data,form_slot_data


