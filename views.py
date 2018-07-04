# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import copy
import json
import operator
from functools import reduce

from django.core.cache import cache
from django.contrib import messages
from django.contrib.admin.utils import label_for_field, help_text_for_field
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.http import urlencode
from django.utils.text import slugify
from django.views.generic import ListView
from django.shortcuts import render, get_object_or_404

from django.core.serializers.json import DjangoJSONEncoder
#from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.module_loading import import_string
from django.utils.html import format_html
from django.contrib.auth.views import redirect_to_login
from django.views.generic.edit import CreateView, UpdateView

from markdown import markdown

# Create your views here.
from docspace.mixins import BaseRequiredMixin
from docspace.models import Article, Taxonomy
from docspace.detail import DetailModelView

from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.utils.html import strip_tags

from docspace.oauth import *


class LatestEntriesFeed(Feed):
    title = "酷特尔"
    link = "/feed/"
    description = "吃饭,睡觉,学习,工作,是你每天最不能忘记的事情。"

    def items(self):
        return Article.objects.order_by('-created')[:10]

    def item_description(self, item):
        value = item.content[:200]
        return strip_tags(value)

def index(request):
    object_list = Article.objects.filter(post_type='post').order_by('-created')
    return render(request, 'index.html', {'objects': object_list})


def archives(request):
    object_list = Article.objects.filter(post_type='post').order_by('-created')
    return render(request, 'archives.html', {'object_list': object_list})


def detail(request, pk):
    post = get_object_or_404(Article, pk=pk)
    post.content = markdown(
        post.content,
        extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
        ])
    return render(request, 'detail.html', context={'post': post})

def author(request, pk):
    object_list = Article.objects.filter(post_type='post', author_id=pk).order_by('-created')
    description_left = "作者：{}".format(request.user)
    return render(request, 'index.html', {'object_list': object_list})

def tag(request, pk):
    object_list = Article.objects.filter(post_type='post', tags__pk=pk).order_by('-created')
    return render(request, 'index.html', {'object_list': object_list})

def category(request, pk):
    object_list = Article.objects.filter(post_type='post', category__pk=pk).order_by('-created')
    return render(request, 'index.html', {'object_list': object_list})


_QUERY = 'search'
_RANGE = 'range'
_ORDER = 'order'
_PAGINATE = 'paginate_by'
_ALL_VAL = 'all'

class IndexView(ListView):

    model = Article

    template_name = 'index.html'

    def has_redirect(self, *args, **kwargs):
        redirect = self.kwargs.pop('redirect', False)
        if redirect:
            opk = self.kwargs.pop('opk')
            url = "http://blog.iloxp.com/{}.html".format(opk)
            tips = '正在为您重定向到 <a id="oldlink" class="text-muted" href="{}">旧页面</a>'.format(url)
            messages.info(self.request, format_html(tips))
        return True

    def get_paginate_by(self, queryset):
        self.paginate_by = self.request.GET.get(_PAGINATE, 20)
        if int(self.paginate_by) > 100:
            messages.warning(self.request, u"仅允许每页最多显示100条数据, 已为您显示100条.")
            self.paginate_by = 100
        return self.paginate_by

    @cached_property
    def get_params(self):
        self.params = dict(self.request.GET.items())
        return self.params

    def get_query_string(self, new_params=None, remove=None):
        new_params = {} if not new_params else new_params
        remove = [] if not remove else remove
        p = self.get_params.copy()
        for r in remove:
            for k in list(p):
                if k.startswith(r):
                    del p[k]
        for k, v in new_params.items():
            if v is None:
                if k in p:
                    del p[k]
            else:
                p[k] = v
        return '?%s' % urlencode(sorted(p.items()))

    def get_filter_by(self):
        effective = {'status': 'published'}
        _fields = dict((f.name, f.attname) for f in self.model._meta.fields)
        for item in _fields:
            if item in self.request.GET:
                effective[_fields[item]] = self.request.GET[item]
                if effective[_fields[item]] == 'all':
                    del effective[_fields[item]]
        return effective

    def get_search_by(self):
        search_by = self.request.GET.get(_QUERY, None)
        return search_by.split(',') if search_by else None

    @cached_property
    def allow_search_fields(self, exclude=None, include=None):
        #include = ['tags__key__icontains']
        opts = self.model._meta
        if not exclude:
            exclude = []
        exclude.extend([f.name for f in opts.fields if getattr(f, 'choices')])
        fields = []
        for f in opts.fields:
            if exclude and f.name in exclude:
                continue
            if isinstance(f, models.ForeignKey):
                submodel = f.related_model
                for sub in submodel._meta.fields:
                    if exclude and sub.name in exclude:
                        continue
                    if isinstance(sub, (models.CharField, models.TextField)) and not getattr(sub, 'choices'):
                        fields.append(f.name+'__'+sub.name+'__icontains')
            if isinstance(f, (models.CharField, models.TextField)):
                fields.append(f.name+'__icontains')
        if include:
            fields.extend(include)
        return fields

    def get_queryset(self):
        queryset = super(IndexView, self).get_queryset()
        search = self.get_search_by()
        effective = self.get_filter_by()
        ordering = self.get_ordering() or ['-pk']
        queryset =self.model.objects.filter(**effective).order_by(*ordering)
        if search:
            lst = []
            for q in search:
                q = q.strip()
                str = [models.Q(**{k: q}) for k in ['title__icontains', 'content__icontains',]]
                #str = [models.Q(**{k: q}) for k in self.allow_search_fields]
                lst.extend(str)
            query_str = reduce(operator.or_, lst)
            queryset = queryset.filter(query_str).order_by(*ordering)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['has_redirect'] = self.has_redirect()
        return context


def OldBlog(request, pk):
    #from django.shortcuts import redirect
    #object_list = Article.objects.filter(post_type='post').order_by('-created')
    view = IndexView.as_view()
    return view(request, redirect=True, opk=int(pk))



class NewModelView(BaseRequiredMixin, SuccessMessageMixin, CreateView):

    def get_template_names(self):
        return ["{0}_new.html".format(self.model_name), "_new.html"]

    def get_permission_required(self):
        self.permission_required = 'docspace.add_%s'%(self.model_name)
        return super(NewModelView, self).get_permission_required()

    def handle_no_permission(self):
        msg = u"您没有新建 {0} 的权限.".format(self.model._meta.verbose_name)
        messages.error(self.request, msg)
        return super(NewModelView, self).handle_no_permission()

    def get_success_message(self, cleaned_data):
        self.success_message = u"成功创建了 {} {}".format(
            self.verbose_name,  self.object
            )
        return self.success_message

    def get_form_class(self):
        name = self.model_name.capitalize()
        try:
            form_class_path = "docspace.forms.{}NewForm".format(name)
            self.form_class = import_string(form_class_path)
        except:
            form_class_path = "docspace.forms.{}Form".format(name)
            self.form_class = import_string(form_class_path)
        return self.form_class

    def get_form_kwargs(self):
        kwargs = super(NewModelView, self).get_form_kwargs()
        params = self.request.GET.dict()
        kwargs.update(**params)
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super(NewModelView, self).form_valid(form)
        #log_action(user=self.request.user, object=self.object, action_flag=u"新增")
        return response

class EditModelView(BaseRequiredMixin, SuccessMessageMixin, UpdateView):
    pass