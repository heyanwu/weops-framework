from django.conf.urls import url
from django.contrib import admin
from django.urls import path

from apps_other.app_bot.views import bot_list, bot_create, bot_detail, bot_update, bot_delete, intent_create, \
    intent_list, intent_delete, intent_update, utterance_create, utterance_list, utterance_delete, utterance_update, \
    story_create, story_list, story_delete, story_update, slot_create, slot_delete, slot_list, \
    slot_update, entity_list, form_create, form_list, form_slot_list, form_delete, formslot_delete, form_update, \
    export_zip, export_to_zip

app_name = 'app_bot'
urlpatterns = [
    path('export/<int:botId>', export_zip, name='export_to_zip'),

    path('bot/', bot_list,name='bot_list'),
    path('bot/create/',bot_create,name = 'bot_create'),
    path('bot/<int:pk>/',bot_detail,name = 'bot_detail'),
    path('bot/update/<int:pk>/',bot_update,name='bot_update'),
    path('bot/delete/<int:pk>/',bot_delete,name = 'bot_delete'),

    path('<int:botId>/entity/', entity_list, name='entity_list'),

    path('<int:botId>/intent/create/', intent_create, name='intent_create'),
    path('<int:botId>/intent/', intent_list, name='intent_list'),
    path('<int:botId>/intent/delete/',intent_delete,name = 'intent_delete'),
    path('<int:botId>/intent/update/<int:intentId>/',intent_update,name = 'intent_update'),

    path('<int:botId>/utterance/create/',utterance_create,name = "utterance_create"),
    path('<int:botId>/utterance/', utterance_list, name='utterance_list'),
    path('<int:botId>/utterance/delete/',utterance_delete,name = 'utterance_delete'),
    path('<int:botId>/utterance/update/<int:utteranceId>/',utterance_update,name = 'utterance_update'),

    path('<int:botId>/story/create/',story_create,name = 'story_create'),
    path('<int:botId>/story/',story_list,name = 'story_list'),
    path('<int:botId>/story/delete/',story_delete,name = 'story_delete'),
    path('<int:botId>/story/update/<int:storyId>/',story_update,name = 'story_update'),

    path('<int:botId>/slot/create/',slot_create,name = 'slot_create'),
    path('<int:botId>/slot/delete/',slot_delete,name = 'slot_delete'),
    path('<int:botId>/slot/',slot_list,name = 'slot_list'),
    path('<int:botId>/slot/update/<int:slotId>/', slot_update, name='slot_update'),

    path('<int:botId>/form/create/',form_create,name = 'form_create'),
    path('<int:botId>/form/',form_list,name = 'form_list'),
    path('<int:botId>/form/<int:formId>',form_slot_list,name = 'form_slot_list'),
    path('<int:botId>/form/delete/',form_delete,name = 'form_delete'),
    path('<int:botId>/<int:forminfoId>/delete/',formslot_delete,name = 'formslot_delete'),
    path('<int:botId>/form/update/<int:formId>/', form_update, name='form_update'),


]