# -*- coding: utf-8 -*-
from django.contrib import admin
from django.db import models
from django.apps import apps
from django.conf import settings
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
# Register your models here.


#admin.AdminSite.site_header = ''
#admin.AdminSite.site_title =' - '


if settings.AUTH_USER_MODEL:
    _label, _model = settings.AUTH_USER_MODEL.split('.')
    User = apps.get_model(app_label=_label, model_name=_model, require_ready=True)
else:
    from django.contrib.auth.models import User


try:
    #app_models = apps.get_app_config('your_app_label').get_models()
    app_models = apps.get_models()
except:
    app_models = None


if app_models:
    exclude_fields = [ 'creator', 'actived', 'deleted', 'modified', 'operator', 'slug', 'content']
    '''exclude_fields = [your hidden fields in here, It's a list.]'''
    for model in app_models:
        if not admin.site.is_registered(model):
            opts = model._meta
            list_filter = []
            search_fields = []
            autocomplete_fields = []
            for f in opts.fields:
                if isinstance(f, (models.BooleanField, models.NullBooleanField)):
                    list_filter.append(f.name)
                if isinstance(f, (models.CharField, models.SlugField, models.TextField)):
                    search_fields.append(f.name)
                if isinstance(f, (models.ForeignKey, models.ManyToManyField)):
                    autocomplete_fields.append(f.name)
            exclude_fields.extend(list_filter)
            options = {
                'autocomplete_fields': autocomplete_fields,
                'list_display': [f.name for f in opts.fields if f.name not in exclude_fields],
                'list_filter' : list_filter,
                #'list_display_links': [nature_field_name(model)],
                'search_fields': search_fields,
                'list_per_page': 20,
                    }
            try:
                admin.site.register(model, **options)
            except:
                pass

if admin.site.is_registered(User):
    admin.site.unregister(User)
    @admin.register(User)
    class UserAdmin(UserAdmin):
        fieldsets = (
            (None, {'fields': ('username', 'password')}),
            (_('Personal info'), {'fields': ('nickname', 'mobile', 'website', 'first_name', 'email', 'last_name')}),
            (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                           'groups', 'user_permissions')}),
            (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        )
        add_fieldsets = (
            (None, {
                'classes': ('wide',),
                'fields': ('username', 'password1', 'password2', 'first_name', 'email'),
            }),
        )

        filter_horizontal = ('groups', 'user_permissions')

if not admin.site.is_registered(Group):
    #admin.site.unregister(Group)
    @admin.register(Group)
    class GroupAdmin(GroupAdmin):
        pass
