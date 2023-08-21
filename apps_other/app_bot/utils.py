from apps_other.app_bot.models import Intent


#生成yml文件
def nlu_yml(request):
    #定义了训练数据，包括意图 (intents) 实体 (entities)
    #先获取数据库中的数据，
    user_id = request.user.id
    data = Intent.objects.filter()