# -*- coding: utf-8 -*-
from django import forms
#from django.contrib.auth.forms import UserCreationForm
from docspace.models import Comment

'''
class Select2Media(object):
    class Media:
        css = {
            'all': (
                '/static/idcops/select2/css/select2.min.css',
                )
            }
        js = (
            '/static/idcops/select2/js/select2.min.js',
            '/static/idcops/select2/js/i18n/zh-CN.js'
            )


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
