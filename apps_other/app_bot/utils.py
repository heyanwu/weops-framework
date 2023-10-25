import ast
import json
import os
import re

import yaml
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps_other.app_bot.models import Intent, Utterance, Story, Slot, FormSlotInfo

#验证json格式数据
def is_valid_json(data):
    try:
        json.loads(data)
        return True
    except json.JSONDecodeError:
        return False

#目的是获取数据，解析成yaml数据
def nlu_yml(botId):
    # 生成YAML内容
    model_data = Intent.objects.all().filter(bot_id=botId).values("name", 'example')
    yaml_data = []
    for item in model_data:
        intent_data = {
            'intent': item['name'],
            'examples': json.loads(item['example'])
        }
        yaml_data.append(intent_data)
    return yaml_data

def response_yml(botId):

    model_data_db = Utterance.objects.filter(bot_id=botId).values_list("name", 'example')

    # 初始化一个空的字典来存储 JSON 数据
    model_data = {}
    model_dic = {}

    # 遍历数据库数据，将文本数据解析为 JSON 并存储在字典中
    for name, example_text in model_data_db:
        try:
            if "utter_valid" in name or "utter_invalid" in name:

                model_data[name] = {
                    "text":example_text
                }
            elif "utter_ask" in name:
                print(example_text)
                example_text = str(example_text).replace("'", "\"").replace('“', '"').replace('”', '"')
                print(example_text)
                example_json = json.loads(example_text)
                model_data[name] = example_json
            else:
                #判断是不是字典类型
                # 检查解析后的数据是否是字典类型
                if "{"in example_text and "}" in example_text:

                    model_dic[name] = json.loads(example_text)
                else:
                    # 尝试将文本数据解析为 JSON 对象
                    example_json = json.loads(example_text)
                    # 将 JSON 对象添加到字典中，以 name 作为键
                    model_data[name] = example_json
        except json.JSONDecodeError as e:
            # 处理解析错误，根据需要执行其他操作
            print(e)
            pass

    return model_data,model_dic

def story_yml(botId):
    model_data = Story.objects.all().filter(bot_id=botId).values("story_type","name", 'example')
    story_data = []
    rule_data = []
    for item in model_data:
        if "story" in item['story_type']:
            data = {
                "story": item["name"],
                "steps":json.loads(item["example"])
            }
            story_data.append(data)

        if "rule" in item['story_type']:
            data = {
                "rule": item["name"],
                "steps": json.loads(item["example"])
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
        matches = re.findall(r'"([^"]*)"', example)
        pattern = r'\[.*?\]\((.*?)\)'
        for example_i in matches:
            entity_matches = re.findall(pattern, example_i)
            if len(entity_matches) != 0:
                # 获取实体数量，都添加进来
                for entity in entity_matches:
                    if entity not in entities_data:
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
        slot_pattern = json.loads(slot.slot_type)
        slot_type = slot_pattern["type"]
        # slot_type = slot_type_switcher[slot_type]
        slots_values = slot_pattern
        slots_values.pop("type")
        influence_conversation = slot.influence
        initial_value = slot.initial_value

        #更换映射类型
        mapping_switcher = {
            "实体":"form_entity",
            "意图":"form_intent",
            "文本":"form_text",
        }
        mappings = json.loads(slot.mapping)
        for mapping in mappings:
            original_type = mapping["type"]
            mapping["type"] = original_type
        if len(slots_values) == 0:
            slots_data[name] = {
                "type":slot_type,
                "influence_conversation":influence_conversation,
                "initial_value":initial_value,
                "mappings":mappings}
        else:
            slots_data[name] = {
                "type": slot_type,
                "values": slots_values,
                "influence_conversation": influence_conversation,
                "initial_value": initial_value,
                "mappings": mappings}

    #获取action，action存在故事里
    action_data = []
    stories = Story.objects.all().filter(bot_id=botId).values('example')
    for story in stories:
        example = story["example"]
        example = json.loads(example)
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

