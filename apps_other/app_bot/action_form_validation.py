import re
from typing import Text, Dict, Any, List

from rasa_sdk import Tracker, Action
from rasa_sdk.executor import CollectingDispatcher

from rasa_sdk.types import DomainDict

# 验证表单的时候，在story或rule中直接写action: action_form_validation即可调用
class ActionFormValidation(Action):

    def name(self) -> Text:
        return "action_form_validation"

    # 获取不同槽的验证值
    def check_data(self, slot_name: Text, slot_value: Any, domain: "DomainDict") -> bool:
        """校验"""
        # 获取槽的类型
        slot_type = domain.get("slots", {}).get(slot_name, {}).get("type")

        # 不同类型槽进行不用的校验
        if slot_type=="text":
            regexp = ""  # 需要填充获取的正则表达式
            if re.match(regexp, slot_value):
                return True
            else:
                return False
        elif slot_type=="boolean":
            if slot_value=="是" or slot_value=="否":
                return True
            else:
                return False
        elif slot_type=="categorical":
            value_list = [] # 需要填充获取的验证值
            if slot_value in value_list:
                return True
            else:
                return False
        elif slot_type=="list":
            value_list = []  # 需要填充获取的验证值
            for value in slot_value:
                if value not in value_list:
                    return False
            return True
        elif slot_type=="float":
            min_value = 0 # 需要填充获取的验证值
            max_value = 0 # 需要填充获取的验证值
            if min_value<=slot_value<=max_value:
                return True
            else:
                return False
        else:
            return False

    async def run(self, dispatcher: "CollectingDispatcher", tracker: Tracker, domain: "DomainDict") -> Dict[Text, Any]:
        """执行表单验证"""
        # 获取表单的槽
        form_slots = tracker.slots
        form_slot_values: {}
        # 表单的配置信息
        form_validations = self.retrieve_config()

        # 遍历表单中的每个槽
        for slot_name in form_slots:
            slot_value = tracker.get_slot(slot_name)
            validation = form_validations.get(slot=slot_name)
            is_required = validation.is_required if validation else False

            if is_required:
                if slot_value is not None:
                    if self.check_data(slot_name, slot_value, domain):
                        form_slot_values[slot_name] = slot_value
                        dispatcher.utter_message(response="utter_effective_tips")
                    else:
                        dispatcher.utter_message(response = "utter_invalid prompt")
                        return {f"{slot_name}": "槽值验证失败"}
                else:
                    dispatcher.utter_message(response = "utter_invalid prompt")
                    return {f"{slot_name}": "槽值不应该为空"}
            else:
                if slot_value is not None:
                    if self.check_data(slot_name, slot_value, domain):
                        dispatcher.utter_message(response = "utter_invalid prompt")
                        return {f"{slot_name}": "槽值验证失败"}
                    else:
                        form_slot_values[slot_name] = slot_value
                        dispatcher.utter_message(response="utter_effective_tips")
                else:
                    form_slot_values[slot_name] = None
                    dispatcher.utter_message(response="utter_effective_tips")

        return form_slot_values

