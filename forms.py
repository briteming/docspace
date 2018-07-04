# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
#from django.contrib.auth.forms import UserCreationForm
from docspace.models import Comment, Article

'''
class FormBaseMixin(Select2Media):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(FormBaseMixin, self).__init__(*args, **kwargs)
        if 'mark' in self.fields:
            self.fields['mark'].widget = forms.HiddenInput()
        if self.user is not None:
            onidc_id = self.user.onidc_id
            effective = {'onidc_id': onidc_id, 'deleted': False, 'actived': True}
            for field_name in self.fields:
                field = self.fields.get(field_name)
                self.fields[field_name].widget.attrs.update({'class': "form-control"})
                if isinstance(field, (forms.fields.SlugField, forms.fields.CharField)):
                    self.fields[field_name].widget.attrs.update({'autocomplete': "off"})
                if isinstance(field, forms.fields.DateTimeField):
                    self.fields[field_name].widget.attrs.update({'data-datetime': "true"})
                if isinstance(field, (forms.models.ModelChoiceField,
                                        forms.models.ModelMultipleChoiceField)):
                    if getattr(field.queryset.model, 'mark', False):
                        field.queryset = shared_queryset(field.queryset, onidc_id)
                        if field.queryset.model is Option:
                            flag = self._meta.model._meta.model_name + field_name
                            field_initial = field.queryset.filter(master=True, flag=flag)
                            if field_initial.exists():
                                field.initial = field_initial.first()
                    else:
                        field.queryset = field.queryset.filter(**effective)
'''

class ArticleNewForm(forms.ModelForm):
    class Media:
        """Media."""
        css_list = [
            'docspace/css/simditor.css',
            'docspace/css/mobile.css',
            'docspace/css/simditor-html.css',
            'docspace/css/simditor-fullscreen.css',
        ]

        jquery_list = ['docspace/js/jquery.min.js',
                       'docspace/js/module.js',
                       'docspace/js/mobilecheck.js',
                       'docspace/js/hotkeys.js',
                       'docspace/js/uploader.js',
                       'docspace/js/simditor.js',
                       'docspace/js/simditor-dropzone.js',
                       'docspace/js/simditor-autosave.js',
                       'docspace/js/simditor-fullscreen.js',
                       'docspace/js/beautify-html.min.js',
                       'docspace/js/simditor-html.js',
                       'docspace/js/simditor-init.js',
                       ]

        css = {
            'all': tuple(
                settings.STATIC_URL + url for url in css_list
                )
            }

        js = tuple(settings.STATIC_URL + url for url in jquery_list)


    class Meta:
        model = Article
        fields = ['title', 'content', 'category', 'tags']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ArticleNewForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)
            self.fields[field_name].widget.attrs.update({'class': "form-control"})
            if isinstance(field, (forms.fields.SlugField, forms.fields.CharField)):
                self.fields[field_name].widget.attrs.update({'autocomplete': "off"})
            if isinstance(field, forms.fields.DateTimeField):
                self.fields[field_name].widget.attrs.update({'data-datetime': "true"})
            _MCF = forms.models.ModelChoiceField
            _MMCF = forms.models.ModelMultipleChoiceField
            if isinstance(field, (_MCF, _MMCF)):
                field.queryset = field.queryset.filter()


class CommentNewForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['parent', 'author_name', 'author_email', 'author_url', 'content']

    def __init__(self, *args, **kwargs):
        super(CommentNewForm, self).__init__(*args, **kwargs)
        self.fields['parent'].widget = forms.HiddenInput()
        self.fields['content'].widget.attrs.update({'rows': 4})
        for field_name in self.fields:
            field = self.fields.get(field_name)
            self.fields[field_name].widget.attrs.update({
                'class': "form-control",
                'placeholder': self.fields[field_name].label,
                })
