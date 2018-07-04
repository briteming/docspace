# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from django.apps import apps
from django.http import Http404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login

# Create your views here.
from docspace.models import Option

logger = logging.getLogger('django.request')


class BaseRequiredMixin(LoginRequiredMixin):

    @staticmethod
    def get_option(key):
        try:
            option = Option.objects.filter(key=key).order_by('-pk')
        except:
            pass
        if option.exists():
            return option.first().value
        return

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, u"需登录系统才能访问")
            return redirect_to_login(
                self.request.get_full_path(),
                self.get_login_url(), self.get_redirect_field_name())
        model = self.kwargs.get('model', None)
        if model:
            try:
                self.model = apps.get_model('docspace', model.lower())
                self.opts = self.model._meta
                self.model_name = self.opts.model_name
                self.verbose_name = self.opts.verbose_name
                if self.kwargs.get('pk', None):
                    self.pk_url_kwarg = self.kwargs.get('pk')
            except:
                raise Http404(u"您访问的模块不存在.")
        return super(BaseRequiredMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        '''SEO Mixin'''
        context = super(BaseRequiredMixin, self).get_context_data(**kwargs)
        meta = {}
        meta['title'] = 1
        meta['keywords'] = 3
        meta['description'] = 3
        context['meta'] = meta
        return context
