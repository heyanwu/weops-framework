from rest_framework import serializers

from apps_other.app_bot.models import Bot, Intent, Utterance, Story

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
