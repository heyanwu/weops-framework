from django.db import migrations


def data_migrate(apps, schema_editor):
    """
    初始化监控采集模版和指标
    """
    activation_model = apps.get_model("activation", "Activation")
    obj = activation_model.objects.first()
    if not obj:
        return
    applications = []
    for i in obj.applications:
        if i in ["health_advisor", "repository", "big_screen"]:
            applications.append(i)
        elif i == "tools":
            applications.extend(["operational_tools", "patch_mgmt", "auto_process"])
        elif i == "resource":
            continue
    applications.append("resource")
    obj.applications = applications
    obj.save()


class Migration(migrations.Migration):
    dependencies = [
        ("activation", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(data_migrate),
    ]
