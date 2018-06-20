# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from docspace.models import Option


class SeoMixin(object):
    '''SEO Mixin'''

    def get_context_data(self, **kwargs):
        context = super(SeoMixin, self).get_context_data(**kwargs)
        meta = {}
        meta['title'] = 1
        meta['keywords'] = 3
        meta['description'] = 3
        context['meta'] = meta
        return context
