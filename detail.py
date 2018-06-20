# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import markdown
import threading
from django.conf import settings
from django.utils.functional import cached_property
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import DetailView
from django.views.generic.edit import FormMixin
from django.utils.text import slugify
from pykismet3 import Akismet
# Create your views here.

from docspace.models import Article
from django.urls import reverse
from docspace.forms import CommentNewForm
'''
hasattr(settings, 'AKISMET_API_KEY')
hasattr(settings, 'SITE_URL')
hasattr(settings, 'CHECK_COMMENT_EMAIL')
'''


api_key = getattr(settings, 'AKISMET_API_KEY', 'd7719929047a')
blog_url = getattr(settings, 'SITE_URL', 'http://www.iloxp.com/')

akismet = Akismet(api_key, blog_url, user_agent='None')


def make_html_message(author, article, url):
    message = '''
    <div style="background-color:#eef2fa; border:1px solid #d8e3e8; color:#111; padding:0 15px; -moz-border-radius:5px; -webkit-border-radius:5px; -khtml-border-radius:5px;">
      <p>{0}, 您好!</p>
      <p>您曾在《{1}》的留言, 有新的回复</p>
      <p>您可以点击<a href="http://www.iloxp.com{2}">查看回复完整內容</a></p>
      <p>(此邮件由系统自动发送，请勿回复.)</p>
    </div>
    '''.format(author, article, url)
    return message


def email_notify(to, content):
    from django.core.mail import send_mail
    return send_mail(
        '您在 酷特尔 博客上的留言有回复啦！',
        'send done...',
        settings.EMAIL_HOST_USER,
        [to],
        html_message=content
    )


def spamcheck(obj, referrer, to, content):
    verify = akismet.check({
        'referrer': referrer,
        'comment_type': 'reply' if obj.parent else 'comment',
        'user_ip': obj.author_ip,
        'user_agent':  obj.agent,
        'comment_content': obj.content,
        'comment_author_email': obj.author_email,
        'comment_author': obj.author_name,
        'is_test': 1,
    })
    obj.approved = 'spam' if verify else 'yes'
    obj.save()
    if not verify:
        email_notify(to, content)
    return obj.approved


class DetailModelView(SuccessMessageMixin, FormMixin, DetailView):

    model = Article

    form_class = CommentNewForm

    template_name = 'detail.html'

    '''
    def get_form_kwargs(self):
        kwargs = super(DetailModelView, self).get_form_kwargs()
        params = self.request.GET.dict()
        kwargs.update(**params)
        kwargs.update({'user': self.request.user})
        return kwargs
    '''

    def get_success_url(self):
        return reverse('detail', kwargs={'pk': self.object.pk})

    def get_success_message(self, cleaned_data):
        self.success_message = "提交成功, 内容正在审核..."
        return self.success_message

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        is_views = self.request.session.get('is_views', [])
        if self.object.pk not in is_views:
            self.object.views_num += 1
            self.object.save()
            is_views.append(self.object.pk)
        self.request.session['is_views'] = is_views
        context = super(DetailModelView, self).get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context

    def get_client_meta(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR', '127.0.0.1')
        agent = self.request.META.get('HTTP_USER_AGENT', '')
        referrer = self.request.META.get('HTTP_REFERER', 'unknown')
        return agent, ip, referrer

    def get_initial(self):
        initial = self.initial.copy()
        initial.update({
            'author_name': self.request.session.get('author_name', None),
            'author_email': self.request.session.get('author_email', None),
            'author_url': self.request.session.get('author_url', None),
        })
        return initial

    def form_valid(self, form):
        agent = self.get_client_meta()[0]
        ipaddr = self.get_client_meta()[1]
        referrer = self.get_client_meta()[2]
        form.instance.agent = agent
        form.instance.author_ip = ipaddr
        if self.request.POST.get('remember', None):
            if self.request.user.is_authenticated:
                form.instance.user = self.request.user
                self.request.session['author_name'] = self.request.user.nature_name
                self.request.session['author_email'] = self.request.user.email
                self.request.session['author_url'] = self.request.user.website_url
            else:
                self.request.session['author_name'] = form.instance.author_name
                self.request.session['author_email'] = form.instance.author_email
                self.request.session['author_url'] = form.instance.author_url
        else:
            del self.request.session['author_name']
            del self.request.session['author_email']
            del self.request.session['author_url']
        form.instance.article = self.object
        form.instance.approved = 'nocheck'
        comment = form.save()
        if comment.parent:
            to_author = comment.parent.author_name
            author_email = comment.parent.author_email
        else:
            to_author = form.instance.author_name
            author_email = form.instance.author_email
        url = '{}#comment-{}'.format(self.get_success_url(), comment.pk)
        html_message = make_html_message(to_author, self.object, url)
        verify = threading.Thread(
            target=spamcheck,
            args=(comment, referrer, author_email, html_message)
                )
        verify.start()
        response = super(DetailModelView, self).form_valid(form)
        return response
