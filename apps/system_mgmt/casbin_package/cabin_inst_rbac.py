# -- coding: utf-8 --

# @File : cabin_inst_rbac.py
# @Time : 2023/7/19 14:12
# @Author : windyzhao

INST_NAMESPACE = "weops_inst_rbac"
INST_MODEL = """
[request_definition]
r = sub, obj, per_type, inst_id
[policy_definition]
p = sub, obj, per_type, inst_id, db_id
[role_definition]
g = _, _
[policy_effect]
e = some(where (p.eft == allow))
[matchers]
m = g(r.sub, p.sub) && r.obj == p.obj && r.per_type == p.per_type && r.inst_id == p.inst_id
"""

# """
# req:
#     user, 实例类型，权限类型，实例Id
# policy:
#     g:
#     username, role_name
# policy:
#     req:
#     user, 实例类型，权限类型，实例Id
#     policy:
#     role_name, 实例类型，查看，1, 模型实例ID1
#     role_name, 实例类型，查看，1, 模型实例ID2
#     role_name, 实例类型，管理 1,  模型实例ID2
# """
