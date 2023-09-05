import re

from rest_framework import serializers

from apps_other.app_bot.models import Bot, Intent, Utterance, Story, Slot, FormSlotInfo, FormInfo


class BotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bot
        fields = '__all__'

class IntentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Intent
        fields = '__all__'

class UtteranceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utterance
        fields = '__all__'

class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = '__all__'


class SlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slot
        fields = '__all__'


#实体序列化
class EntitySerializer(serializers.ModelSerializer):
    entity = serializers.SerializerMethodField()

    class Meta():
        model = Intent
        fields = ['name','entity','bot_id']

    def get_entity(self,obj):
        example = obj.example
        if example:
            pattern = r'\[.*?\]\((.*?)\)'
            matches = []
            for item in example:
                if isinstance(item, str):
                    item_matches = re.findall(pattern, item)
                    matches.extend(item_matches)
            return matches
        return []

class SlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slot
        fields = '__all__'

class FormSlotInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormSlotInfo
        fields = '__all__'

class FormInfoSerializer(serializers.ModelSerializer):
    slots = serializers.PrimaryKeyRelatedField(queryset=Slot.objects.all(), many=True, required=False)
    class Meta:
        model = FormInfo
        fields = '__all__'

