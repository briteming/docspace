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


CODE_LANGUAGES = [
    { "name": 'Bash', "value": 'bash' },
    { "name": 'Python', "value": 'python' },
    { "name": 'JavaScript', "value": 'js' },
    { "name": 'HTML,XML', "value": 'html' },
    { "name": 'JSON', "value": 'json' },
    { "name": 'YAML', "value": 'yaml' },
    { "name": 'Markdown', "value": 'markdown' },
    { "name": 'CSS', "value": 'css' },
    { "name": 'Visual Basic', "value": 'visual-basic' },
    { "name": 'PowerShell', "value": 'powershell' },
    { "name": 'Diff', "value": 'diff' },
    { "name": 'Ruby', "value": 'ruby' },
    { "name": 'SQL', "value": 'sql' },
    { "name": 'PHP', "value": 'php' },
    { "name": 'C#', "value": 'cs' },
    { "name": 'C++', "value": 'c++' },
    { "name": 'Erlang', "value": 'erlang' },
    { "name": 'Less', "value": 'less' },
    { "name": 'Sass', "value": 'sass' },
    { "name": 'CoffeeScript', "value": 'coffeescript' },
    { "name": 'Java', "value": 'java' },
    { "name": 'Objective C', "value": 'oc' },
    { "name": 'Perl', "value": 'parl' },
]