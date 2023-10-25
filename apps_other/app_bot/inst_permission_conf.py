from apps_other.app_bot.models import Bot
from apps_other.app_bot.serializers import BotSerializer


class BotInstPermissions:
    id = "机器人--语料管理"
    model = Bot
    fields = {"name": "标题", "id": "", "created_User": "创建人", "created_Date": "创建时间"}  # 查询模型字段
    search = "name"
    permissions = {"view": "查询", "manage": "管理"}
    serializer = BotSerializer