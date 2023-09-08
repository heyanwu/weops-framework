import io
import json
import os
import shutil
import tempfile

import zipfile
from datetime import timedelta

import yaml
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponse, FileResponse
from django.shortcuts import redirect, render
from drf_yasg import openapi
from minio import Minio, S3Error
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from django.db import connection, transaction

import local_settings
from .models import Bot, Intent, Utterance, Story, Slot, FormInfo, FormSlotInfo
from .serializers import BotSerializer, IntentSerializer, UtteranceSerializer, StorySerializer, SlotSerializer, \
    EntitySerializer, FormInfoSerializer, FormSlotInfoSerializer
from .utils import nlu_yml, response_yml, story_yml, domain_yml
from .minio_utils import MinIoClient


#导出接口
#data:nlu.yml,rule.yml,story.yml,response.yml

#Bot1 :data文件夹，action.py,domain.yml,config.yml

def export_to_zip(request,botId):
    # 创建临时文件夹
    temp_dir = tempfile.mkdtemp()

    # 创建 "Data" 文件夹
    data_folder = os.path.join(temp_dir, "Data")
    os.makedirs(data_folder, exist_ok=True)

    # 生成YAML内容
    nlu_data = nlu_yml(botId)
    response_data,response_dict = response_yml(botId)
    story_data,rule_data = story_yml(botId)
    intents_data,entities_data,slots_data,action_data,form_slot_data = domain_yml(botId)

    # 将docs/config.yml的默认配置文件config.yml复制到临时文件夹中
    local_config = "apps_other/app_bot/config.yml"
    temp_yaml_path = os.path.join(temp_dir, "config.yml")
    shutil.copy2(local_config, temp_yaml_path)

    # 将actions的默认配置文件action.py复制到临时文件夹中
    local_action = "apps_other/app_bot/action_form_validation.py"
    temp_yaml_path = os.path.join(temp_dir, "action.py")
    shutil.copy2(local_action, temp_yaml_path)

    #domain.yml
    yaml_file_path = os.path.join(temp_dir, "domain.yml")
    with open(yaml_file_path, "w",encoding="utf-8") as yaml_file:
        yaml_file.write(f'version: "3.1"\n\n')
        yaml_file.write(f'intents:\n')
        yaml_content = yaml.dump(intents_data, indent=2, sort_keys=False, allow_unicode=True)
        indented_yaml_str = "\n".join("  " + line for line in yaml_content.splitlines())
        yaml_file.write(indented_yaml_str)

        yaml_file.write(f'\nentities:\n')
        yaml_content = yaml.dump(entities_data, indent=2, sort_keys=False, allow_unicode=True)
        indented_yaml_str = "\n".join("  " + line for line in yaml_content.splitlines())
        yaml_file.write(indented_yaml_str)

        yaml_file.write('\nresponses:\n')
        for key, value in response_data.items():
            if isinstance(value, list):
                yaml_file.write(f'  {key}:\n')
                for item in value:
                    yaml_file.write(f'    - text: "{item}"\n')
            elif isinstance(value, dict):
                yaml_file.write(f'  {key}:\n')
                for sub_key, sub_value in value.items():
                    yaml_file.write(f'    - {sub_key}: "{sub_value}"\n')
        if len(response_dict) != 0:
            yaml_content = yaml.dump(response_dict, indent=2, sort_keys=False, allow_unicode=True)
            indented_yaml_str = "\n".join("  " + line for line in yaml_content.splitlines())
            yaml_file.write(indented_yaml_str)

        yaml_file.write(f'\nslots:\n')
        yaml_content = yaml.dump(slots_data, indent=2,sort_keys=False, allow_unicode=True)
        indented_yaml_str = "\n".join("  " + line for line in yaml_content.splitlines())
        yaml_file.write(indented_yaml_str)

        yaml_file.write(f'\nactions:\n')
        yaml_content = yaml.dump(action_data, indent=2, sort_keys=False, allow_unicode=True)
        indented_yaml_str = "\n".join("  " + line for line in yaml_content.splitlines())
        yaml_file.write(indented_yaml_str)

        yaml_file.write(f'forms:\n')
        yaml_content = yaml.dump(form_slot_data, indent=2, sort_keys=False, allow_unicode=True)
        indented_yaml_str = "\n".join("  " + line for line in yaml_content.splitlines())
        yaml_file.write(indented_yaml_str)

    # nlu.yml文件
    yaml_file_path = os.path.join(data_folder, "nlu.yml")
    with open(yaml_file_path, "w",encoding="utf-8") as yaml_file:
        yaml_file.write(f'version: "3.1"\n')
        yaml_file.write('nlu:' + '\n')
        for nlu in nlu_data:
            yaml_file.write('- intent: ' + nlu["intent"] + '\n')
            yaml_file.write(f"  examples: |\n")
            for example in nlu["examples"]:
                yaml_file.write('    - ' + example + '\n')


    # response.yml文件
    yaml_file_path = os.path.join(data_folder, "response.yml")
    with open(yaml_file_path, "w",encoding="utf-8") as yaml_file:
        yaml_file.write(f'version: "3.1"\nresponses:\n')
        for key, value in response_data.items():
            if isinstance(value, list):
                yaml_file.write(f'  {key}:\n')
                for item in value:
                    yaml_file.write(f'    - text: "{item}"\n')
            elif isinstance(value, dict):
                yaml_file.write(f'  {key}:\n')
                for sub_key, sub_value in value.items():
                    yaml_file.write(f'    - {sub_key}: "{sub_value}"\n')
        if len(response_dict) != 0:
            yaml_content = yaml.dump(response_dict, indent=2, sort_keys=False, allow_unicode=True)
            indented_yaml_str = "\n".join("  " + line for line in yaml_content.splitlines())
            yaml_file.write(indented_yaml_str)


    # stories.yml文件
    yaml_file_path = os.path.join(data_folder, "stories.yml")
    with open(yaml_file_path, "w",encoding="utf-8") as yaml_file:
        yaml_file.write(f'version: "3.1"\n')
        yaml_file.write('stories:' + '\n')
        for story in story_data:
            yaml_file.write('- story: ' + story["story"] + '\n')
            yaml_file.write('  steps:' + '\n')
            for key,value in story["steps"].items():
                yaml_file.write('  - ' + key + ': ' + yaml.dump(value, default_style='plain',sort_keys=True, allow_unicode=True))

    # rules.yml文件
    yaml_file_path = os.path.join(data_folder, "rules.yml")
    with open(yaml_file_path, "w",encoding="utf-8") as yaml_file:
        yaml_file.write(f'version: "3.1"\nrules:\n')
        for rule in rule_data:
            yaml_file.write('- rule: ' + rule["rule"] + '\n')
            yaml_file.write('  steps:' + '\n')
            for key, value in rule["steps"].items():
                yaml_file.write('  - ' + key + ': ' + yaml.dump(value, default_style='plain', sort_keys=True,
                                                                    allow_unicode=True))

    # 创建ZIP文件
    in_memory_zip = io.BytesIO()
    with zipfile.ZipFile(in_memory_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for folder_root, _, filenames in os.walk(temp_dir):
            for filename in filenames:
                file_path = os.path.join(folder_root, filename)
                arcname = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arcname)

    # 删除临时文件夹
    shutil.rmtree(temp_dir)

    # 创建HTTP响应，将ZIP文件作为附件返回
    response = HttpResponse(in_memory_zip.getvalue(), content_type='application/zip')

    # 设置响应头，将文件名改为 "bot.zip"
    response['Content-Disposition'] = 'attachment; filename=bot.zip'

    return response

'''
def export_zip(request,botId):
    # 创建临时文件夹
    temp_dir = tempfile.mkdtemp()

    # 创建 "Data" 文件夹
    data_folder = os.path.join(temp_dir, "Data")
    os.makedirs(data_folder, exist_ok=True)

    # 生成YAML内容
    nlu_data = nlu_yml(botId)
    # response_data = response_yml(botId)
    # story_data, rule_data = story_yml(botId)
    # intents_data, entities_data, slots_data, action_data, form_slot_data = domain_yml(botId)

    # 将docs/config.yml的默认配置文件config.yml复制到临时文件夹中
    local_config = "apps_other/app_bot/config.yml"
    temp_yaml_path = os.path.join(temp_dir, "config.yml")
    shutil.copy2(local_config, temp_yaml_path)

    # 将actions的默认配置文件action.py复制到临时文件夹中
    local_action = "apps_other/app_bot/action_form_validation.py"
    temp_yaml_path = os.path.join(temp_dir, "action.py")
    shutil.copy2(local_action, temp_yaml_path)

    # domain.yml
    yaml_file_path = os.path.join(temp_dir, "domain.yml")
    with open(yaml_file_path, "w") as yaml_file:
        yaml_file.write(f'version: "3.1"\n\n')
        yaml_file.write(f'intents:\n')
        yaml.dump(intents_data, yaml_file, sort_keys=False, allow_unicode=True)
        yaml_file.write(f'entities:\n')
        yaml.dump(entities_data, yaml_file, sort_keys=False, allow_unicode=True)
        yaml_file.write(f'slots:\n')
        yaml_content = yaml.dump(slots_data, indent=2, sort_keys=False, allow_unicode=True)
        indented_yaml_str = "\n".join("  " + line for line in yaml_content.splitlines())
        yaml_file.write(indented_yaml_str)
        yaml_file.write(f'\nactions:\n')
        yaml.dump(action_data, yaml_file, sort_keys=False, allow_unicode=True)
        yaml_file.write(f'forms:\n')
        yaml_content = yaml.dump(form_slot_data, indent=2, sort_keys=False, allow_unicode=True)
        indented_yaml_str = "\n".join("  " + line for line in yaml_content.splitlines())
        yaml_file.write(indented_yaml_str)

    # nlu.yml文件
    yaml_file_path = os.path.join(data_folder, "nlu.yml")
    with open(yaml_file_path, "w") as yaml_file:
        yaml_file.write(f'version: "3.1"\n')
        yaml_file.write('nlu:' + '\n')
        for nlu in nlu_data:
            yaml_file.write('- intent: ' + nlu["intent"] + '\n')
            yaml_file.write(f"  examples: |\n")
            for example in nlu["examples"]:
                yaml_file.write('    - ' + example + '\n')
    
    # response.yml文件
    yaml_file_path = os.path.join(data_folder, "response.yml")
    with open(yaml_file_path, "w") as yaml_file:
        yaml_file.write(f'version: "3.1"\n\n')
        yaml.safe_dump(response_data, yaml_file, sort_keys=False, allow_unicode=True, indent=2)

    # stories.yml文件
    yaml_file_path = os.path.join(data_folder, "stories.yml")
    with open(yaml_file_path, "w") as yaml_file:
        yaml_file.write(f'version: "3.1"\n')
        yaml_file.write('stories:' + '\n')
        for story in story_data:
            yaml_file.write('- story: ' + story["story"] + '\n')
            yaml_file.write('  steps:' + '\n')
            for key, value in story["steps"].items():
                yaml_file.write(
                    '  - ' + key + ': ' + yaml.dump(value, default_style='plain', sort_keys=True, allow_unicode=True))

    # rules.yml文件
    yaml_file_path = os.path.join(data_folder, "rules.yml")
    with open(yaml_file_path, "w") as yaml_file:
        yaml_file.write(f'version: "3.1"\nrules:\n')
        for rule in rule_data:
            yaml_file.write('- rule: ' + rule["rule"] + '\n')
            yaml_file.write('  steps:' + '\n')
            for key, value in rule["steps"].items():
                yaml_file.write('  - ' + key + ': ' + yaml.dump(value, default_style='plain', sort_keys=True,
                                                                allow_unicode=True))
    # 创建ZIP文件
    in_memory_zip = io.BytesIO()
    with zipfile.ZipFile(in_memory_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for folder_root, _, filenames in os.walk(temp_dir):
            for filename in filenames:
                file_path = os.path.join(folder_root, filename)
                arcname = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arcname)

    #检查桶是否存在
    minio_client = MinIoClient()
    if not minio_client.bucket_exists(bucket_name = "bot"):
        minio_client.make_bucket(bucket_name = "bot")

    zip_file_path = os.path.join(temp_dir, 'bot.zip')
    with open(zip_file_path, 'wb') as f:
        f.write(in_memory_zip.getvalue())
    object_name = f'{botId}/bot.zip'  # 指定在Minio中的对象名称

    #上传文件到Minio
    minio_client.fput_object("bot",object_name,zip_file_path)

    # 删除临时文件夹
    shutil.rmtree(temp_dir)

    #下载文件链接
    result_data = minio_client.presigned_get_object(bucket_name = "bot",object_name=object_name)
    if result_data["result"]:
        # 构建文件响应并返回
        response = FileResponse(minio_client.get_object("bot", object_name))
        response['Content-Disposition'] = f'attachment; filename="{object_name}"'
        return response
    else:
        return HttpResponse("下载失败")
'''

#获取机器人列表
@swagger_auto_schema(
    method='get',
    responses={
        '200': BotSerializer,
        '401': 'Unauthorized',
        '404': 'Not Found',
    },
    operation_description='获取bot列表接口',
    operation_id='bot_list',
    tags=['机器人'],
    deprecated=False,
)
@api_view(['get'])
@transaction.atomic
def bot_list(request):
    bots = Bot.objects.all()
    serializer = BotSerializer(bots,many=True)
    return Response(serializer.data)

#创建机器人
@swagger_auto_schema(
    method='post',  #指定装饰器应该应用于哪些请求方法（GET、POST、PUT、DELETE 等）
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'icon': openapi.Schema(type=openapi.TYPE_STRING, example='FirstIcon',description="图标索引"),
            'name': openapi.Schema(type=openapi.TYPE_STRING, example='ml',description="名字"),
            'introduction': openapi.Schema(type=openapi.TYPE_STRING, example="firstBot",description="简介"),
            'created_User': openapi.Schema(type=openapi.TYPE_STRING, example="me",description="用户创建者"),
        },
        required=['icon','name','created_User'],
    ),
    responses={
        '200': BotSerializer,
        '401': 'Unauthorized',
        '404': 'Not Found',
    },  #用于指定不同响应状态码的详细说明
    operation_description='创建bot接口',    #用于为操作提供更详细的说明
    operation_id='bot_create',  #指定操作的唯一标识符，通常是一个字符串
    tags=['机器人'],   #用于为 API 操作指定标签
    deprecated=False,   #用于标记一个 API 操作是否已被弃用
)
@api_view(['post'])
@transaction.atomic
def bot_create(request):
    data = request.data
    serializer = BotSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data,status=201)
    return Response(serializer.errors,status=400)

#更新机器人
@swagger_auto_schema(
    method='put',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'icon': openapi.Schema(type=openapi.TYPE_STRING, example='FirstIcon', description="图标索引"),
            'name': openapi.Schema(type=openapi.TYPE_STRING, example='ml', description="名字"),
            'introduction': openapi.Schema(type=openapi.TYPE_STRING, example="firstBot", description="简介"),
            'created_User': openapi.Schema(type=openapi.TYPE_STRING, example="me", description="用户创建者"),
        },
        required=['icon', 'name', 'created_User'],
    ),
    responses={
        '200': BotSerializer,
        '401': 'Unauthorized',
        '404': 'Not Found',
    },
    operation_description='更新bot接口',
    operation_id='bot_update',
    tags=['机器人'],
    deprecated=False,
)
@api_view(['put'])
@transaction.atomic
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
@swagger_auto_schema(
    method='get',
    responses={
        '200': BotSerializer,
        '401': 'Unauthorized',
        '404': 'Not Found',
    },
    operation_description='获取bot详细内容接口',
    operation_id='bot_detail',
    tags=['机器人'],
    deprecated=False,
)
@api_view(['get'])
@transaction.atomic
def bot_detail(request,pk):
    try:
        bot = Bot.objects.get(pk=pk)
    except Bot.DoesNotExist:
        return Response(status=404)

    serializer = BotSerializer(bot)
    return Response(serializer.data)

#删除机器人
@swagger_auto_schema(
    method='delete',
    responses={
        '200': "successful",
        '401': 'Unauthorized',
        '404': 'Not Found',
    },
    operation_description='删除bot',
    operation_id='bot_delete',
    tags=['机器人'],
    deprecated=False,
)
@api_view(['delete'])
@transaction.atomic
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
@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'name': openapi.Schema(type=openapi.TYPE_STRING, description="名字"),
            'example': openapi.Schema(type=openapi.TYPE_STRING, description="简介"),
            'bot': openapi.Schema(type=openapi.TYPE_INTEGER, description="隶属bot"),
        },
        example={
                  "bot": 1,
                  "example": [
                    "我想要买一个pizza",
                    "pizza",
                    "买pizza"
                  ],
                  "name": "buy_pizza"
            },
        required=['name'],
    ),
    responses={
        '200': IntentSerializer,
        '401': 'Unauthorized',
        '404': 'Not Found',
    },
    operation_description='创建intent接口',
    operation_id='intent_create',
    tags=['意图'],
    deprecated=False,
)
@api_view(['POST'])
@transaction.atomic
def intent_create(request,botId):
        try:
            intentOb = request.data
            intent = Intent()
            intent.name = intentOb.get("name")
            try:
                intent.example = intentOb.get("example")
            except:
                intent.example = None
            intent.bot = Bot.objects.get(id=botId)
            serializer = IntentSerializer(data={'name': intent.name, 'example':intent.example,'bot': intent.bot.pk})
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Object created successfully."}, status=200)
            else:
                return Response(serializer.errors, status=401)
        except Exception as e:
            print(e)
            return Response({"message": "An error occurred."}, status=401)


#获取意图的所有内容
@swagger_auto_schema(
    method='get',
    responses={
        '200': IntentSerializer,
        '401': 'Unauthorized',
        '404': 'Not Found',
    },
    operation_description='获取intent列表接口',
    operation_id='intent_list',
    tags=['意图'],
    deprecated=False,
)
@api_view(['get'])
@transaction.atomic
def intent_list(request,botId):
    intents = Intent.objects.all().filter(bot_id=botId)
    serializer = IntentSerializer(intents, many=True)
    return Response(serializer.data)

#删除意图
@swagger_auto_schema(
    method='delete',
    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'intent_ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_INTEGER)),
        },
        example={
            "intent_ids": [1, 2, 3]
        },
        required=['intent_ids']
    ),
    responses={
        '200': "successful",
        '404': 'No objects deleted',
        '500': 'An error occurred',
    },
    operation_description='删除intents',
    operation_id='intent_delete',
    tags=['意图'],
    deprecated=False,
)
@api_view(['delete'])
@transaction.atomic
def intent_delete(request,botId):
    try:
        # 从请求的数据中获取要删除的故事ID列表
        intent_ids_to_delete = request.data.get('intent_ids', [])

        # 使用filter批量删除满足条件的故事
        intents = Intent.objects.filter(pk__in=intent_ids_to_delete, bot_id=botId)
        deleted_count = intents.delete()[0]  # 执行删除操作，获取受影响的行数

        if deleted_count > 0:
            return JsonResponse({"message": f"{deleted_count} objects deleted successfully."})
        else:
            return JsonResponse({"message": "No objects deleted."}, status=404)
    except Exception as e:
        print(e)  # 这里可以打印其他异常信息以帮助调试
        return JsonResponse({"message": "An error occurred."}, status=500)



#意图更新
@swagger_auto_schema(
    method='put',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'name': openapi.Schema(type=openapi.TYPE_STRING, description="名字"),
            'example': openapi.Schema(type=openapi.TYPE_STRING, description="简介"),
            'bot': openapi.Schema(type=openapi.TYPE_INTEGER, description="隶属bot"),
        },
        example={
            "bot": 1,
            "example": [
                "我想要买一个pizza",
                "pizza",
                "买pizza"
            ],
            "name": "buy_pizza"
        },
        required=['name'],
    ),
    responses={
        '200': IntentSerializer,
        '401': 'Unauthorized',
        '404': 'Not Found',
    },
    operation_description='更新intent接口',
    operation_id='intent_update',
    tags=['意图'],
    deprecated=False,
)
@api_view(['put'])
@transaction.atomic
def intent_update(request, botId,intentId):
    try:
        intentObject = Intent.objects.get(pk=intentId)
    except Intent.DoesNotExist:
        return Response(status=404)
    intentOb = request.data
    intent = Intent()
    intent.name = intentOb.get("name")
    try:
        intent.example = intentOb.get("example")
    except:
        pass
    intent.bot = Bot.objects.get(id=botId)
    serializer = IntentSerializer(intentObject,data={'name':intent.name,'bot':intent.bot.id,"example":intent.example})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    else:
        return Response(serializer.errors, status=400)

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'name': openapi.Schema(type=openapi.TYPE_STRING, description="名字"),
            'example': openapi.Schema(type=openapi.TYPE_STRING, description="简介"),
            'bot': openapi.Schema(type=openapi.TYPE_INTEGER, description="隶属bot"),
        },
        example={
            'name': 'utter_res',
            'example': [{
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
                    ],
            'bot': 1,
        },
        required=['name'],
    ),
    responses={
        '200': UtteranceSerializer,
        '401': 'Unauthorized',
        '404': 'Not Found',
    },
    operation_description='创建utterance接口',
    operation_id='utterance_create',
    tags=['响应'],
    deprecated=False,
)
#新增响应
@api_view(['POST'])
@transaction.atomic
def utterance_create(request,botId):
    try:
        utteranceOb = request.data
        utterance = Utterance()
        utterance.name = utteranceOb["name"]
        try:
            utterance.example = utteranceOb["example"]
        except:
            utterance.example = None
        utterance.bot = Bot.objects.get(id=botId)
        serializer = UtteranceSerializer(data={'name': utterance.name, 'example':utterance.example,'bot': utterance.bot.pk})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=400)
    except Exception as e:
        print(e)
        return Response({"message": "An error occurred."}, status=401)

@swagger_auto_schema(
    method='get',
    responses={
        '200': UtteranceSerializer,
        '401': 'Unauthorized',
        '404': 'Not Found',
    },
    operation_description='获取utterance列表接口',
    operation_id='utterance_list',
    tags=['响应'],
    deprecated=False,
)
#获取响应的所有内容
@api_view(['get'])
@transaction.atomic
def utterance_list(request,botId):
    utterances = Utterance.objects.all().filter(bot_id=botId)
    serializer = UtteranceSerializer(utterances, many=True)
    return Response(serializer.data)

#响应删除
@swagger_auto_schema(
    method='delete',
    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'utterance_ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_INTEGER)),
        },
        example={
            "utterance_ids": [1, 2, 3]
        },
        required=['utterance_ids']
    ),
    responses={
        '200': "successful",
        '404': 'No objects deleted',
        '500': 'An error occurred',
    },
    operation_description='删除utterances',
    operation_id='utterance_delete',
    tags=['响应'],
    deprecated=False,
)
@api_view(['delete'])
@transaction.atomic
def utterance_delete(request,botId):
    try:
        # 从请求的数据中获取要删除的故事ID列表
        utterance_ids_to_delete = request.data.get('utterance_ids', [])

        # 使用filter批量删除满足条件的故事
        utterances = Utterance.objects.filter(pk__in=utterance_ids_to_delete, bot_id=botId)
        deleted_count = utterances.delete()[0]  # 执行删除操作，获取受影响的行数

        if deleted_count > 0:
            return JsonResponse({"message": f"{deleted_count} objects deleted successfully."})
        else:
            return JsonResponse({"message": "No objects deleted."}, status=404)
    except Exception as e:
        print(e)  # 这里可以打印其他异常信息以帮助调试
        return JsonResponse({"message": "An error occurred."}, status=500)

#响应更新
@swagger_auto_schema(
    method='put',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'name': openapi.Schema(type=openapi.TYPE_STRING, description="名字"),
            'example': openapi.Schema(type=openapi.TYPE_STRING, description="简介"),
            'bot': openapi.Schema(type=openapi.TYPE_INTEGER, description="隶属bot"),
        },
        example={
            'name': 'firstIntent',
            'example': [{
                "text": "Here is an example message with buttons and a link.",
                "buttons": [
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
                "buttons_link": [
                    {
                        "title": "Visit our website",
                        "url": "https://example.com"
                    }
                ]
            }
            ],
            'bot': 1,
        },
        required=['name'],
    ),
    responses={
        '200': UtteranceSerializer,
        '401': 'Unauthorized',
        '404': 'Not Found',
    },
    operation_description='更新utterance接口',
    operation_id='utterance_update',
    tags=['响应'],
    deprecated=False,
)
@api_view(['put'])
@transaction.atomic
def utterance_update(request, botId,utteranceId):
    try:
        utteranceObject = Utterance.objects.get(pk=utteranceId)
    except ObjectDoesNotExist:
        return JsonResponse({"message": "Object not found."}, status=404)
    utteranceOb = request.data
    utterance = Utterance()
    utterance.name = utteranceOb.get("name")
    try:
        utterance.example = utteranceOb.get("example")
    except:
        pass
    utterance.bot = Bot.objects.get(id=botId)
    serializer = UtteranceSerializer(utteranceObject,data={'name':utterance.name,'bot':utterance.bot.id,"example":utterance.example})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    else:
        return Response(serializer.errors, status=400)

#故事类
#新建一个故事

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'icon': openapi.Schema(type=openapi.TYPE_STRING, description="图标索引"),
            'name': openapi.Schema(type=openapi.TYPE_STRING, description="名字"),
            'story_type': openapi.Schema(type=openapi.TYPE_STRING, description="故事类型"),
            'example': openapi.Schema(type=openapi.TYPE_STRING, description="样例"),
            'bot': openapi.Schema(type=openapi.TYPE_INTEGER, description="隶属bot"),
        },
        example={
            'icon': '1',
            'name': 'active_pizza_form',
            'story_type':'story',
            'example': {
                "intent":'buy_pizza',
                'action':"pizza_form",
                'active_loop':'pizza_form',
            },
            'bot': 1,
        },
        required=['icon','name','story_type'],
    ),
    responses={
        '200': StorySerializer,
        '401': 'Unauthorized',
        '404': 'Not Found',
    },
    operation_description='创建story接口',
    operation_id='story_create',
    tags=['故事'],
    deprecated=False,
)
#创建一个故事
@api_view(['POST'])
@transaction.atomic
def story_create(request,botId):
    storiesOb = request.data
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
        data={'icon':stories.icon,'name': stories.name, 'story_type':stories.story_type,'example': stories.example, 'bot': stories.bot.pk})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    else:
        return Response(serializer.errors, status=401)


@swagger_auto_schema(
    method='get',
    responses={
        '200': StorySerializer,
        '401': 'Unauthorized',
        '404': 'Not Found',
    },
    operation_description='获取story列表接口',
    operation_id='story_list',
    tags=['故事'],
    deprecated=False,
)
#获取故事的列表
@api_view(['get'])
@transaction.atomic
def story_list(request,botId):
    #根据botId查询里面的故事数量
    stories = Story.objects.all().filter(bot_id=botId)
    serializer = StorySerializer(stories, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

#故事的删除
@swagger_auto_schema(
    method='delete',
    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'story_ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_INTEGER)),
        },
        example={
            "story_ids": [1, 2, 3]
        },
        required=['story_ids']
    ),
    responses={
        '200': "successful",
        '404': 'No objects deleted',
        '500': 'An error occurred',
    },
    operation_description='删除stories',
    operation_id='stories_delete',
    tags=['故事'],
    deprecated=False,
)
@api_view(['delete'])
@transaction.atomic
def story_delete(request,botId):
    try:
        # 从请求的数据中获取要删除的故事ID列表
        story_ids_to_delete = request.data.get('story_ids', [])

        # 使用filter批量删除满足条件的故事
        stories = Story.objects.filter(pk__in=story_ids_to_delete, bot_id=botId)
        deleted_count = stories.delete()[0]  # 执行删除操作，获取受影响的行数

        if deleted_count > 0:
            return JsonResponse({"message": f"{deleted_count} objects deleted successfully."})
        else:
            return JsonResponse({"message": "No objects deleted."}, status=404)
    except Exception as e:
        print(e)  # 这里可以打印其他异常信息以帮助调试
        return JsonResponse({"message": "An error occurred."}, status=500)


#故事更新
@swagger_auto_schema(
    method='put',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'icon': openapi.Schema(type=openapi.TYPE_STRING, description="图标索引"),
            'name': openapi.Schema(type=openapi.TYPE_STRING, description="名字"),
            'story_type': openapi.Schema(type=openapi.TYPE_STRING, description="故事类型"),
            'example': openapi.Schema(type=openapi.TYPE_STRING, description="样例"),
            'bot': openapi.Schema(type=openapi.TYPE_INTEGER, description="隶属bot"),
        },
        example={
            'icon': '1',
            'name': 'firstStory',
            'story_type': 'rule',
            'example': {
                "intent":'buy_pizza',
                'action':"pizza_form",
                'active_loop':'pizza_form',
            },
            'bot': 1,
        },
        required=['icon', 'name', 'story_type'],
    ),
    responses={
        '200': StorySerializer,
        '401': 'Unauthorized',
        '404': 'Not Found',
    },
    operation_description='更新story接口',
    operation_id='story_update',
    tags=['故事'],
    deprecated=False,
)
@api_view(['put'])
@transaction.atomic
def story_update(request, botId,storyId):
    try:
        storiesObject = Story.objects.get(pk=storyId)
    except Story.DoesNotExist:
        return Response(status=404)
    storiesOb = request.data
    stories = Story()
    stories.icon = storiesOb.get('icon')
    stories.name = storiesOb.get('name')
    stories.story_type = storiesOb.get('story_type')
    stories.example = storiesOb.get('example')
    stories.bot = Bot.objects.get(id=botId)
    serializer = StorySerializer(storiesObject,
                                 data={'icon':stories.icon,'name': stories.name, 'story_type':stories.story_type,'example': stories.example, 'bot': stories.bot.pk})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    else:
        return Response(serializer.errors, status=400)

#新建一个槽
@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'name': openapi.Schema(type=openapi.TYPE_STRING, description="名字"),
            'slot_type': openapi.Schema(type=openapi.TYPE_STRING, description="槽类型"),
            "initial_value":openapi.Schema(type=openapi.TYPE_STRING, description="初始值"),
            "influence":openapi.Schema(type=openapi.TYPE_STRING, description="影响对话"),
            'mapping': openapi.Schema(type=openapi.TYPE_STRING, description="映射"),
            'bot': openapi.Schema(type=openapi.TYPE_INTEGER, description="隶属bot"),

        },
        example={
            'name': 'firstSlot',
            'slot_type':{
                "type":"数值",
                "min_value":0,
                "max_value":255,
            },
            "initial_value":10,
            "influence":True,
            'mapping':[{
               "type":"实体",
                "entity":"color",
                "intent":"pizza size",
                "no_intent":"greet",
            },
            {
               "type":"意图",
                "value":"intent",
                "intent":"pizza size",
                "no_intent":"greet",
            },
            ],
            'bot': 1,
        },
        required=['name','slot_type',"mapping","initial_value"],
    ),
    responses={
        '200': SlotSerializer,
        '401': 'Unauthorized',
        '404': 'Not Found',
    },
    operation_description='创建slot接口',
    operation_id='slot_create',
    tags=['槽'],
    deprecated=False,
)
@api_view(['POST'])
@transaction.atomic
def slot_create(request,botId):
    slotsOb = request.data
    slot = Slot()
    slot.name = slotsOb["name"]
    slot.slot_type = slotsOb['slot_type']
    slot.mapping = slotsOb['mapping']
    for item in slot.mapping:
        #验证映射类型
        if item["type"] == "实体":
            try:
                item["entity"]
            except:
                return Response({"message":"映射为实体类时，请选择实体"}, status=401)
        elif item["type"] == "意图":
            try:
                item["value"]
            except:
                return Response({"message":"映射为意图类时，请填入值"}, status=401)
    slot.initial_value = slotsOb['initial_value']
    slot.bot = Bot.objects.get(id=botId)
    try:
        slot.influence = slotsOb['influence']
    except:
        slot.influence = True
    slot.bot = Bot.objects.get(id=botId)

    serializer = SlotSerializer(
        data={'name': slot.name, 'slot_type':slot.slot_type,'influence': slot.influence,"initial_value":slot.initial_value,"mapping":slot.mapping, 'bot': slot.bot.pk})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=200)
    else:
        return Response(serializer.errors, status=401)

#槽的删除
@swagger_auto_schema(
    method='delete',
    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'slot_ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_INTEGER)),
        },
        example={
            "slot_ids": [1, 2, 3]
        },
        required=['slot_ids']
    ),
    responses={
        '200': "successful",
        '404': 'No objects deleted',
        '500': 'An error occurred',
    },
    operation_description='删除slots',
    operation_id='slot_delete',
    tags=['槽'],
    deprecated=False,
)
@api_view(['delete'])
@transaction.atomic
def slot_delete(request,botId):
    try:
        # 从请求的数据中获取要删除的故事ID列表
        slot_ids_to_delete = request.data.get('slot_ids', [])

        # 使用filter批量删除满足条件的故事
        slots = Slot.objects.filter(pk__in=slot_ids_to_delete, bot_id=botId)
        deleted_count = slots.delete()[0]  # 执行删除操作，获取受影响的行数

        if deleted_count > 0:
            return JsonResponse({"message": f"{deleted_count} objects deleted successfully."})
        else:
            return JsonResponse({"message": "No objects deleted."}, status=404)
    except Exception as e:
        print(e)  # 这里可以打印其他异常信息以帮助调试
        return JsonResponse({"message": "An error occurred."}, status=500)

@swagger_auto_schema(
    method='get',
    responses={
        '200': SlotSerializer,
        '401': 'Unauthorized',
        '404': 'Not Found',
    },
    operation_description='获取slot列表接口',
    operation_id='slot_list',
    tags=['槽'],
    deprecated=False,
)
#获取槽的列表
@api_view(['get'])
@transaction.atomic
def slot_list(request,botId):
    #根据botId查询里面的故事数量
    slots = Slot.objects.all().filter(bot_id=botId)
    serializer = SlotSerializer(slots, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

#槽更新
@swagger_auto_schema(
    method='put',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'name': openapi.Schema(type=openapi.TYPE_STRING, description="名字"),
            'slot_type': openapi.Schema(type=openapi.TYPE_STRING, description="槽类型"),
            "initial_value": openapi.Schema(type=openapi.TYPE_STRING, description="初始值"),
            "influence": openapi.Schema(type=openapi.TYPE_STRING, description="影响对话"),
            'mapping': openapi.Schema(type=openapi.TYPE_STRING, description="映射"),
            'bot': openapi.Schema(type=openapi.TYPE_INTEGER, description="隶属bot"),

        },
        example={
            'name': 'firstSlot',
            'slot_type': {
                "type": "数值",
                "min_value": 0,
                "max_value": 255,
            },
            "initial_value": 10,
            "influence": True,
            'mapping': [{
                "type": "实体",
                "entity": "color",
                "intent": "pizza size",
                "no_intent": "greet",
            },
                {
                    "type": "意图",
                    "value": "intent",
                    "intent": "pizza size",
                    "no_intent": "greet",
                },
            ],
            'bot': 1,
        },
        required=['name', 'slot_type', "mapping", "initial_value"],
    ),
    responses={
        '200': SlotSerializer,
        '401': 'Unauthorized',
        '404': 'Not Found',
    },
    operation_description='更新slot接口',
    operation_id='slot_update',
    tags=['槽'],
    deprecated=False,
)
@api_view(['put'])
@transaction.atomic
def slot_update(request, botId,slotId):
    try:
        slotsObject = Slot.objects.get(pk=slotId)
    except Slot.DoesNotExist:
        return Response(status=404)

    slotsOb = request.data
    slot = Slot()
    slot.name = slotsOb["name"]
    slot.slot_type = slotsOb['slot_type']
    slot.mapping = slotsOb['mapping']
    for item in slot.mapping:
        # 验证映射类型
        if item["type"] == "实体":
            try:
                item["entity"]
            except:
                return Response({"message": "映射为实体类时，请选择实体"}, status=401)
        elif item["type"] == "意图":
            try:
                item["value"]
            except:
                return Response({"message": "映射为意图类时，请填入值"}, status=401)
    slot.initial_value = slotsOb['initial_value']
    slot.bot = Bot.objects.get(id=botId)
    try:
        slot.influence = slotsOb['influence']
    except:
        slot.influence = True
    slot.bot = Bot.objects.get(id=botId)

    serializer = SlotSerializer(slotsObject,data={'name': slot.name, 'slot_type':slot.slot_type,'influence': slot.influence,"initial_value":slot.initial_value,"mapping":slot.mapping, 'bot': slot.bot.pk})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    else:
        return Response(serializer.errors, status=400)

#获取实体接口
#获取意图的所有内容
@swagger_auto_schema(
    method='get',
    responses={
        '200': EntitySerializer,
        '401': 'Unauthorized',
        '404': 'Not Found',
    },
    operation_description='获取实体列表接口',
    operation_id='entity_list',
    tags=['实体'],
    deprecated=False,
)
@api_view(['get'])
@transaction.atomic
def entity_list(request,botId):
    intents = Intent.objects.all().filter(bot_id=botId)
    serializer = EntitySerializer(intents, many=True)
    return Response(serializer.data)

#创建一个表单
@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'form_info': openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'bot': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'name': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            'form_slot_info': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'slot_name': openapi.Schema(type=openapi.TYPE_STRING),
                        'validation': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING)
                        ),
                        'question': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING)
                        ),
                        'valid_prompts': openapi.Schema(type=openapi.TYPE_STRING),
                        'invalid_prompts': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        },
        example={
            'form_info': {
                'bot': 1,
                'name': 'Sample Form'
            },
            'form_slot_info': [
                {
                    'slot_name': 'pizza_a',
                    'validation': ['value1', 'value2'],
                    'question': ['What is your favorite color?'],
                    'valid_prompts': 'Valid answer examples',
                    'invalid_prompts': 'Invalid answer examples'
                },
                {
                    'slot_name': 'pizza_b',
                    'validation': ['value1', 'value2'],
                    'question': ['What is your age?'],
                    'valid_prompts': 'Valid answer examples',
                    'invalid_prompts': 'Invalid answer examples'
                }
            ]
        },
    ),
    responses={
        '200': 'Create Successful',
        '401': 'Unauthorized',
        '404': 'Not Found',
    },
    operation_description='创建form接口',
    operation_id='form_create',
    tags=['表单'],
    deprecated=False,
)
@api_view(['POST'])
def form_create(request,botId):
    form_info_data = request.data.get("form_info")
    form_info_serializer = FormInfoSerializer(data=form_info_data)

    try:
        if form_info_serializer.is_valid():
            form_info_instance = form_info_serializer.save()  # 保存FormInfo实例到数据库，获取一个有效的ID

            try:
                form_slot_info_data = request.data.get("form_slot_info")
                for item in form_slot_info_data:
                    slot_name = item['slot_name']
                    slot = Slot.objects.get(name=slot_name)
                    form_info_instance.slots.add(slot)  # 建立多对多关系

                    form_slot_info = FormSlotInfo()
                    form_slot_info.slot = slot
                    form_slot_info.forminfo = form_info_instance
                    form_slot_info.validation = item["validation"]
                    form_slot_info.question = item["question"]
                    form_slot_info.valid_prompts = item["valid_prompts"]
                    form_slot_info.invalid_prompts = item["invalid_prompts"]

                    # 存槽详细信息
                    form_slot_info_serializer = FormSlotInfoSerializer(data={
                        "validation": form_slot_info.validation,
                        "question": form_slot_info.question,
                        "valid_prompts": form_slot_info.valid_prompts,
                        "invalid_prompts": form_slot_info.invalid_prompts,
                        "forminfo": form_slot_info.forminfo.pk,
                        "slot": form_slot_info.slot.pk,
                    })
                    if form_slot_info_serializer.is_valid():
                        form_slot_info_serializer.save()

                        # 同时将询问问题放在响应中

                        utter_ask_name = f"utter_ask_{slot_name}"
                        bot_id = form_slot_info.slot.bot_id
                        question = form_slot_info.question

                        if question.startswith('"') and question.endswith('"'):
                            question = question[1:-1]
                        question = json.loads(question)
                        utterance_ask, created = Utterance.objects.get_or_create(name=utter_ask_name, example=question,
                                                                                 bot_id=bot_id)
                        utterance_ask.save()

                        utter_valid_name = f"utter_valid_{slot_name}"
                        utter_invalid_name = f"utter_invalid_{slot_name}"
                        valid = form_slot_info.valid_prompts
                        invalid = form_slot_info.invalid_prompts
                        utterance_valid, created = Utterance.objects.get_or_create(name=utter_valid_name, example=valid,
                                                                                   bot_id=bot_id)
                        utterance_valid.save()

                        utterance_invalid, created = Utterance.objects.get_or_create(name=utter_invalid_name,
                                                                                     example=invalid,
                                                                                     bot_id=bot_id)
                        utterance_invalid.save()
                    else:
                        return Response(form_slot_info_serializer.errors, status=401)
                return Response("保存成功表单和槽详细信息.", status=200)
            except:
                return Response({"message": "保存表单成功,但是没有保存槽"}, status=201)
        else:
            # 表单信息不合法
            return Response(form_info_serializer.errors, status=401)
    except Exception as e:
        # 其他异常情况
        print(e)
        return Response({"message": "保存失败"}, status=500)


#获取表单列表
@swagger_auto_schema(
    method='get',
    responses={
        '200': FormInfoSerializer,
        '401': 'Unauthorized',
        '404': 'Not Found',
    },
    operation_description='获取表单列表接口',
    operation_id='form_list',
    tags=['表单'],
    deprecated=False,
)
#获取表单的列表
@api_view(['get'])
@transaction.atomic
def form_list(request,botId):
    #获取FormInfo的数据
    forminfos = FormInfo.objects.all().filter(bot_id=botId)
    serializer = FormInfoSerializer(forminfos, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

#根据表单id和槽id查找槽详细信息
@swagger_auto_schema(
    method='get',
    responses={
        '200': FormSlotInfoSerializer,
        '401': 'Unauthorized',
        '404': 'Not Found',
    },
    operation_description='获取表单中的槽详细信息接口',
    operation_id='form_slot_list',
    tags=['表单'],
    deprecated=False,
)
#获取表单的详细信息
@api_view(['get'])
@transaction.atomic
def form_slot_list(request,botId,formId):
    #获取FormInfo的数据
    formslotinfos = FormSlotInfo.objects.all().filter(forminfo_id=formId)
    serializer = FormSlotInfoSerializer(formslotinfos, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

#删除表单
@swagger_auto_schema(
    method='delete',
    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'form_ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_INTEGER)),
        },
        example={
            "form_ids": [1, 2, 3]
        },
        required=['form_ids']
    ),
    responses={
        '200': "successful",
        '404': 'No objects deleted',
        '500': 'An error occurred',
    },
    operation_description='删除forms',
    operation_id='form_delete',
    tags=['表单'],
    deprecated=False,
)
@api_view(['delete'])
@transaction.atomic
def form_delete(request,botId):
    try:
        # 从请求的数据中获取要删除的表单ID列表
        form_ids_to_delete = request.data.get('form_ids', [])

        # 使用filter批量删除满足条件的表单
        forms = FormInfo.objects.filter(pk__in=form_ids_to_delete, bot_id=botId)
        deleted_count = forms.delete()[0]  # 执行删除操作，获取受影响的行数

        if deleted_count > 0:
            return JsonResponse({"message": f"{deleted_count} objects deleted successfully."})
        else:
            return JsonResponse({"message": "No objects deleted."}, status=404)
    except Exception as e:
        print(e)  # 这里可以打印其他异常信息以帮助调试
        return JsonResponse({"message": "An error occurred."}, status=500)


#删除表单中槽详细信息
@swagger_auto_schema(
    method='delete',
    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'formslot_ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_INTEGER)),
        },
        example={
            "formslot_ids": [1, 2, 3]
        },
        required=['formslot_ids']
    ),
    responses={
        '200': "successful",
        '404': 'No objects deleted',
        '500': 'An error occurred',
    },
    operation_description='删除formslots',
    operation_id='formslot_delete',
    tags=['表单'],
    deprecated=False,
)
@api_view(['delete'])
@transaction.atomic
def formslot_delete(request,botId,forminfoId):
    try:
        # 从请求的数据中获取要删除的表单槽详细信息的ID列表
        formslot_ids_to_delete = request.data.get('formslot_ids', [])

        # 使用filter批量删除满足条件的槽详细信息
        formslots = FormSlotInfo.objects.filter(pk__in=formslot_ids_to_delete, forminfo_id=forminfoId)

        #同时删除关联关系表中的数据
        #根据formslots获取slot_id
        slot_ids = formslots.values_list("slot_id",flat=True)

        with connection.cursor() as cursor:
            for slotId in slot_ids:
                cursor.execute("DELETE FROM app_bot_forminfo_slots WHERE slot_id = %s AND forminfo_id = %s",(slotId, forminfoId))

        deleted_count = formslots.delete()[0]  # 执行删除操作，获取受影响的行数

        if deleted_count > 0:
            return JsonResponse({"message": f"{deleted_count} objects deleted successfully."})
        else:
            return JsonResponse({"message": "No objects deleted."}, status=404)
    except Exception as e:
        print(e)  # 这里可以打印其他异常信息以帮助调试
        return JsonResponse({"message": "An error occurred."}, status=500)

#表单更新
@swagger_auto_schema(
    method='put',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'form_info': openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'bt': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'naome': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            'form_slot_info': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'slot_name': openapi.Schema(type=openapi.TYPE_STRING),
                        'validation': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING)
                        ),
                        'question': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING)
                        ),
                        'valid_prompts': openapi.Schema(type=openapi.TYPE_STRING),
                        'invalid_prompts': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        },
        example={
            'form_info': {
                'bot': 1,
                'name': 'Sample Form'
            },
            'form_slot_info': [
                {
                    'slot_name': 'Slotf',
                    'validation': ['value1', 'value2'],
                    'question': ['What is your favorite color?'],
                    'valid_prompts': 'Valid answer examples',
                    'invalid_prompts': 'Invalid answer examples'
                },
                {
                    'slot_name': 'Slotg',
                    'validation': ['value1', 'value2'],
                    'question': ['What is your age?'],
                    'valid_prompts': 'Valid answer examples',
                    'invalid_prompts': 'Invalid answer examples'
                }
            ]
        },
    ),
    responses={
        '200': 'Create Successful',
        '401': 'Unauthorized',
        '404': 'Not Found',
    },
    operation_description='更新form接口',
    operation_id='form_update',
    tags=['表单'],
    deprecated=False,
)
@api_view(['put'])
@transaction.atomic
def form_update(request, botId, formId):
    try:
        formObject = FormInfo.objects.get(pk=formId)
    except FormInfo.DoesNotExist:
        return Response(status=404)

    #表单信息
    formOb = request.data.get("form_info")
    forminfo = FormInfo()
    forminfo.bot = Bot.objects.get(id = botId)
    forminfo.name = formOb["name"]

    forminfoserializer = FormInfoSerializer(formObject,data={"name":forminfo.name,"bot":forminfo.bot.pk})
    if forminfoserializer.is_valid():
        form_info_instance = forminfoserializer.save()
    try:
        form_slot_info_data = request.data.get("form_slot_info")
        for item in form_slot_info_data:
            slot_name = item['slot_name']
            slot = Slot.objects.get(name=slot_name)

            #判断一下数据库中是否有这个槽详细信息
            if not form_info_instance.slots.all().filter(pk=slot.pk).exists():
                form_info_instance.slots.add(slot)  # 建立多对多关系

                form_slot_info = FormSlotInfo()
                form_slot_info.slot = slot
                form_slot_info.forminfo = form_info_instance
                form_slot_info.validation = item["validation"]
                form_slot_info.question = item["question"]
                form_slot_info.valid_prompts = item["valid_prompts"]
                form_slot_info.invalid_prompts = item["invalid_prompts"]

                # 存槽详细信息
                form_slot_info_serializer = FormSlotInfoSerializer(data={
                    "validation": form_slot_info.validation,
                    "question": form_slot_info.question,
                    "valid_prompts": form_slot_info.valid_prompts,
                    "invalid_prompts": form_slot_info.invalid_prompts,
                    "forminfo": form_slot_info.forminfo.pk,
                    "slot": form_slot_info.slot.pk,
                })
                if form_slot_info_serializer.is_valid():
                    form_slot_info_serializer.save()

                    # 同时将询问问题放在响应中
                    utter_name = "utter_ask_" + slot_name
                    utterance, created = Utterance.objects.get_or_create(name=utter_name,bot_id=botId)
                    # 将问题放在text中
                    question_list = []
                    for question_data in form_slot_info.question:
                        question_list.append({
                            "text": question_data,
                        })
                    utterance.example = question_list
                    utterance.bot = Bot.objects.get(id=botId)
                    serializer = UtteranceSerializer(
                        data={ 'example': utterance.example, 'bot': utterance.bot.pk})
                    if serializer.is_valid():
                        serializer.save()
                    else:
                        return Response(serializer.errors, status=401)
                else:
                    return Response(form_slot_info_serializer.errors, status=401)
            else:

                formslotObject = FormSlotInfo.objects.get(forminfo_id=formObject.pk,slot_id=slot.pk)
                form_slot_info = FormSlotInfo()
                form_slot_info.slot = slot
                form_slot_info.forminfo = form_info_instance
                form_slot_info.validation = item["validation"]
                form_slot_info.question = item["question"]
                form_slot_info.valid_prompts = item["valid_prompts"]
                form_slot_info.invalid_prompts = item["invalid_prompts"]

                # 存槽详细信息
                form_slot_info_serializer = FormSlotInfoSerializer(formslotObject,data={
                    "validation": form_slot_info.validation,
                    "question": form_slot_info.question,
                    "valid_prompts": form_slot_info.valid_prompts,
                    "invalid_prompts": form_slot_info.invalid_prompts,
                    "forminfo": form_slot_info.forminfo.pk,
                    "slot": form_slot_info.slot.pk,
                })
                if form_slot_info_serializer.is_valid():
                    form_slot_info_serializer.save()
                    # 同时将询问问题放在响应中

                    utter_ask_name = f"utter_ask_{slot_name}"
                    bot_id = form_slot_info.slot.bot_id
                    question = form_slot_info.question

                    if question.startswith('"') and question.endswith('"'):
                        question = question[1:-1]
                    question = json.loads(question)
                    utterance_ask, created = Utterance.objects.get_or_create(name=utter_ask_name, example=question,
                                                                             bot_id=bot_id)
                    utterance_ask.save()

                    utter_valid_name = f"utter_valid_{slot_name}"
                    utter_invalid_name = f"utter_invalid_{slot_name}"
                    valid = form_slot_info.valid_prompts
                    invalid = form_slot_info.invalid_prompts
                    utterance_valid, created = Utterance.objects.get_or_create(name=utter_valid_name, example=valid,
                                                                               bot_id=bot_id)
                    utterance_valid.save()

                    utterance_invalid, created = Utterance.objects.get_or_create(name=utter_invalid_name,
                                                                                 example=invalid,
                                                                                 bot_id=bot_id)
                    utterance_invalid.save()

                else:
                    return Response(form_slot_info_serializer.errors, status=401)

        return Response("更新成功表单和槽详细信息.", status=200)
    except Exception as e:
        print(e)
        return Response({"message": "未更新成功", "error": str(e)}, status=201)
