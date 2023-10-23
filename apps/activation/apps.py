# -- coding: utf-8 --


import datetime
import json
import os

from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import ugettext_lazy as _

from apps.activation.helper import aes_encrypt, create_registration_code
from apps.activation.utils.constants import MENUS_MAPPING
from utils.decorators import catch_exception


class ActivationConfig(AppConfig):
    name = "apps.activation"
    verbose_name = _("activation")

    def ready(self):
        post_migrate.connect(ActivationsInit.init_activation, sender=self)


class ActivationsInit(object):
    @staticmethod
    @catch_exception
    def init_activation(sender, **kwargs):
        from apps.activation.models import Activation

        if Activation.objects.all().exists():
            return

        registration_code = create_registration_code()
        start_time = datetime.datetime.now()
        expiration_time = start_time + datetime.timedelta(days=30)
        start_date = str(start_time.date())
        expiration_time = str(expiration_time.date())
        obj_data = {
            "registration_code": registration_code,
            "start_date": start_date,
            "expiration_date": expiration_time,
            "activation_status": "试用期",
            "agent_num": 50,
            "applications": ["resource"] + list(MENUS_MAPPING.keys()),
        }
        activation_code = aes_encrypt(json.dumps(obj_data))
        obj_data["activation_code"] = activation_code
        Activation.objects.create(**obj_data)

        file_path = "USERRES/never_delete"
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                first_date = aes_encrypt(start_date)
                f.write(first_date)
