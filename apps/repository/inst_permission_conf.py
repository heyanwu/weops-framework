from apps.repository.models import Repository
from apps.repository.serializers import RepositoryInstPermissionsSerializer
from apps.system_mgmt.constants import BASIC_MONITOR
from apps_other.app_bot.models import Bot
from apps_other.app_bot.serializers import BotSerializer

class RepositoryInstPermissions():
    id = "知识库"  # 实例类型
    model = Repository  # 模型
    search_inst_list = [{"知识库": Repository}]
    fields = {"title": "文章标题", "id": "", "created_by": "创建人", "created_at": "创建时间"}  # 查询模型字段
    search = "title"  # 搜索字段
    default_filter = {"drafts": False}
    permissions = {"view": "查询", "manage": "管理"}
    serializer = RepositoryInstPermissionsSerializer