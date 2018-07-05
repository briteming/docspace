# -*- coding: utf-8 -*-
from django.apps import AppConfig


class DocspaceConfig(AppConfig):
    name = 'docspace'
    verbose_name = u"DS博客"

    def ready(self):
        from docspace import signals