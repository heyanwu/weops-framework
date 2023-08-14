import json
import os
import random

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from . import models
from blueapps.account.models import User
from blueapps.conf import settings
from rest_framework import viewsets, mixins

from .models import Bot, Intent, Utterance, Story
from .serializers import BotSerializer, IntentSerializer, UtteranceSerializer, StorySerializer



#获取机器人列表
@api_view(['GET'])
def bot_list(request):
    bots = Bot.objects.all()
    serializer = BotSerializer(bots,many=True)
    return Response(serializer.data)

#创建机器人
@api_view(['POST'])
def bot_create(request):
    data = request.data
    serializer = BotSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data,status=201)
    return Response(serializer.errors,status=400)

#更新机器人
@api_view(['PUT'])
def bot_update(request, pk):
    try:
        bot = Bot.objects.get(pk=pk)
    except Bot.DoesNotExist:
        return Response(status=404)

    serializer = BotSerializer(bot, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

#查询机器人详细内容
@api_view(['GET'])
def bot_detail(request,pk):
    try:
        bot = Bot.objects.get(pk=pk)
    except Bot.DoesNotExist:
        return Response(status=404)

    serializer = BotSerializer(bot)
    return Response(serializer.data)

#删除机器人
@api_view(['DELETE'])
def bot_delete(request,pk):
    try:
        bot = Bot.objects.get(pk=pk)
        bot.delete()
        return JsonResponse({"message": "Object deleted successfully."})
    except ObjectDoesNotExist:
        return JsonResponse({"message": "Object not found."}, status=404)
    except Exception as e:
        print(e)  # 这里可以打印其他异常信息以帮助调试
        return JsonResponse({"message": "An error occurred."}, status=500)


#对意图进行操作
#首先是创建一个新的意图
'''
{
    "intent":{
                "name":"oracledb",
                "example":["Oracle发生Oracle数据库应用类等待时间告警", 
                    "[192.168.1.100](ip_address)\"上的Oracle数据库应用类等待时间异常",
                    "发生Oracle数据库应用类等待时间告警,ip地址:\"[10.0.0.1](ip_address)"]
            }
    
}
'''
@api_view(['POST'])
def intent_create(request,botId):
    if request.method == "POST":
        try:
            datas = request.data
            intentOb = datas.get('intent')
            intent = Intent()
            intent.name = intentOb.get("name")
            try:
                intent.example = intentOb.get("example")
                print(type(intent.example))
            except:
                intent.example = None
            intent.bot = Bot.objects.get(id=botId)
            serializer = IntentSerializer(data={'name': intent.name, 'example':intent.example,'app_bot': intent.bot.pk})
            if serializer.is_valid():
                serializer.save()
            return Response({"message": "Object created successfully."}, status=201)
        except Exception as e:
            print(e)
    return Response(serializer.errors,status=400)

#获取意图的所有内容
@api_view(['GET'])
def intent_list(request,botId):
    intents = Intent.objects.all().filter(bot_id=botId)
    serializer = IntentSerializer(intents, many=True)
    return Response(serializer.data)

#删除某个意图
@api_view(['DELETE'])
def intent_delete(request,botId,intentId):
    try:
        intent = Intent.objects.get(pk=intentId)
        intent.delete()
        return JsonResponse({"message": "Object deleted successfully."})
    except ObjectDoesNotExist:
        return JsonResponse({"message": "Object not found."}, status=404)
    except Exception as e:
        print(e)  # 这里可以打印其他异常信息以帮助调试
        return JsonResponse({"message": "An error occurred."}, status=500)

#意图更新
@api_view(['POST'])
def intent_update(request, botId,intentId):
    try:
        intentObject = Intent.objects.get(pk=intentId)
    except Intent.DoesNotExist:
        return Response(status=404)
    datas = request.data
    intentOb = datas.get('intent')
    intent = Intent()
    intent.name = intentOb.get("name")
    try:
        intent.example = intentOb.get("example")
    except:
        pass
    intent.bot = Bot.objects.get(id=botId)
    serializer = IntentSerializer(intentObject,data={'name':intent.name,'app_bot':intent.bot.id,"example":intent.example})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response


#响应格式
'''
{
    "utterance":{
                    "name":"utter_eexample",
                    "example":[{
                        "text": "Here is an example message with buttons and a link.",
                        "buttons":[
                                {
                                    "title": "Button 1",
                                    "payload": "/button1"
                                }
                                ,
                                {
                                    "title": "Button 2",
                                    "payload": "/button2"
                                } 
                        ],
                        "image": "https://example.com/image.png",
                        "buttons_link":[
                                {
                                    "title": "Visit our website",
                                    "url": "https://example.com"
                                }
                        ]
                    }
                    ]
                }
}
'''
#新增响应
@api_view(['POST'])
def utterance_create(request,botId):
        datas = request.data
        utteranceOb = datas.get('utterance')
        utterance = Utterance()
        utterance.name = utteranceOb["name"]
        try:
            utterance.example = utteranceOb["example"]
        except:
            utterance.example = None
        utterance.bot = Bot.objects.get(id=botId)
        serializer = UtteranceSerializer(data={'name': utterance.name, 'example':utterance.example,'app_bot': utterance.bot.pk})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors,status=400)

#获取响应的所有内容
@api_view(['GET'])
def utterance_list(request,botId):
    utterances = Utterance.objects.all().filter(bot_id=botId)
    serializer = UtteranceSerializer(utterances, many=True)
    return Response(serializer.data)

#响应删除
@api_view(['DELETE'])
def utterance_delete(request,botId,utteranceId):
    try:
        utterance = Utterance.objects.get(pk=utteranceId)
        utterance.delete()
        return JsonResponse({"message": "Object deleted successfully."})
    except ObjectDoesNotExist:
        return JsonResponse({"message": "Object not found."}, status=404)
    except Exception as e:
        print(e)  # 这里可以打印其他异常信息以帮助调试
        return JsonResponse({"message": "An error occurred."}, status=500)

#响应更新
@api_view(['POST'])
def utterance_update(request, botId,utteranceId):
    try:
        utteranceObject = Utterance.objects.get(pk=utteranceId)
    except ObjectDoesNotExist:
        return JsonResponse({"message": "Object not found."}, status=404)
    datas = request.data
    utteranceOb = datas.get('utterance')
    utterance = Utterance()
    utterance.name = utteranceOb.get("name")
    try:
        utterance.example = utteranceOb.get("example")
    except:
        pass
    utterance.bot = Bot.objects.get(id=botId)
    serializer = UtteranceSerializer(utteranceObject,data={'name':utterance.name,'app_bot':utterance.bot.id,"example":utterance.example})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response({'message': 'Batch update successful.'}, status=status.HTTP_200_OK)

#故事类

#新建一个故事，内容包括
'''
举例：
{
    "story":{
        "icon":"firstIcon",
        "name":"thirdName",
        "story_type":"auto",
        "example":[
            {
                "intent":{
                    "name":"firstIntent",
                    "pointToObject":""
                }
            },
            {

                "utterance":{
                    "name":"utterance",
                    "pointToObject":""
                }
            }
        ]
    }
}
'''

#创建一个故事
@api_view(['POST'])
def story_create(request,botId):
    datas = request.data
    storiesOb = datas.get('stories')
    stories = Story()
    stories.icon = storiesOb['icon']
    stories.name = storiesOb["name"]
    stories.story_type = storiesOb['story_type']
    try:
        stories.example = storiesOb["example"]
    except:
        stories.example = None
    stories.bot = Bot.objects.get(id=botId)
    serializer = StorySerializer(
        data={'icon':stories.icon,'name': stories.name, 'story_type':stories.story_type,'example': stories.example, 'app_bot': stories.bot.pk})
    if serializer.is_valid():
        # serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

#获取故事的列表
@api_view(['GET'])
def story_list(request,botId):
    #根据botId查询里面的故事数量
    stories = Story.objects.all().filter(bot_id=botId)
    serializer = StorySerializer(stories, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

#故事的删除
@api_view(['DELETE'])
def story_delete(request,botId,storyId):
    try:
        story = Story.objects.get(pk=storyId)
        story.delete()
        return JsonResponse({"message": "Object deleted successfully."})
    except ObjectDoesNotExist:
        return JsonResponse({"message": "Object not found."}, status=404)
    except Exception as e:
        print(e)  # 这里可以打印其他异常信息以帮助调试
        return JsonResponse({"message": "An error occurred."}, status=500)


#故事更新
@api_view(['POST'])
def story_update(request, botId,storyId):
    try:
        storiesObject = Story.objects.get(pk=storyId)
    except Story.DoesNotExist:
        return Response(status=404)
    datas = request.data
    storiesOb = datas.get('stories')
    stories = Story()
    stories.icon = storiesOb.get('icon')
    stories.name = storiesOb.get('name')
    stories.story_type = storiesOb.get('story_type')
    stories.example = storiesOb.get('example')
    stories.bot = Bot.objects.get(id=botId)
    serializer = StorySerializer(storiesObject,
                                 data={'icon':stories.icon,'name': stories.name, 'story_type':stories.story_type,'example': stories.example, 'app_bot': stories.bot.pk})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(status=200)


