# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.dispatch import receiver
from django.db.models import signals
from django.conf import settings
from docspace.models import Comment



@receiver(signals.post_save, sender=Comment)
def update_article_comment_count(instance, **kwargs):
    article = instance.article
    approved = instance.approved
    _model = instance._meta.model
    count = _model.objects.filter(approved='yes', article=article).count()
    if article.comment_num != count:
        article.comment_num = count
        article.save()

@receiver(signals.post_save, sender=Comment)
def on_comment_was_posted(sender, *args, **kwargs):
    article = instance.article
    approved = instance.approved
    _model = instance._meta.model
    try:
        from akismet import Akismet
    except:
        from pykismet3 import Akismet
    except:
        return
        
    AKISMET_API_KEY = getattr(settings, 'AKISMET_API_KEY', 'd7719929047a')
    SITE_URL = getattr(settings, 'SITE_URL', 'http://www.iloxp.com/')
    akismet = Akismet(AKISMET_API_KEY, SITE_URL, user_agent='Mozilla/5.0')
    verify = akismet.check({
        'referrer': '127.0.0.1',
        'comment_type': 'reply' if instance.parent else 'comment',
        'user_ip': instance.author_ip,
        'user_agent':  instance.agent,
        'comment_content': instance.content,
        'is_test': 1,
        if instance.author_email:
            'comment_author_email': instance.author_email,
        if instance.author_name:
            'comment_author': instance.author_name,
    })
    instance.approved = 'spam' if verify else 'yes'
    instance.save()
    if not verify:
        
        email_notify(to, content)
    return instance.approved
