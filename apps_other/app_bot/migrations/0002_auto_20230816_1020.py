# Generated by Django 2.2.6 on 2023-08-16 10:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_bot', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bot',
            old_name='creatDate',
            new_name='created_Date',
        ),
        migrations.RenameField(
            model_name='bot',
            old_name='creatUser',
            new_name='created_User',
        ),
    ]
