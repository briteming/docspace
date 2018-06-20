# -*- coding: utf-8 -*-
from pykismet3 import Akismet
import threading

api_key = 'd7719929047a'
blog_url = 'http://www.iloxp.com/'
akismet = Akismet(api_key, blog_url, user_agent='None')

def spamcheck(obj, referrer):
    comment_type = 'comment'
    if obj.parent:
        comment_type = 'reply'
    verify = akismet.check({
        'referrer': referrer,
        'comment_type': comment_type,
        'user_ip': obj.author_ip,
        'user_agent':  obj.agent,
        'comment_content': obj.content,
        'comment_author_email': obj.author_email,
        'comment_author': obj.author_name,
        'is_test': 1,
        })
    if verify:
        obj.approved = 'spam'
    else:
        obj.approved = 'yes'
    obj.save()
    return obj.approved
