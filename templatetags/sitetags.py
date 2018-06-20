# -*- coding: utf-8 -*-
import re
import os
import requests
from PIL import Image
from io import BytesIO
import hashlib
import random
from django.utils.http import urlencode
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _, ngettext, pgettext

from docspace.models import Option, Link

register = template.Library()


DEFAULT_GRAVATR_URL = getattr(settings, 'DEFAULT_GRAVATR_URL', None)


# return only the URL of the gravatar
# TEMPLATE USE:  {{ email|gravatar_url:150 }}
@register.filter
def gravatar_url(email, size=40):
    if DEFAULT_GRAVATR_URL:
        default = DEFAULT_GRAVATR_URL
    else:
        default = random.choice(["retro", "monsterid", "wavatar", "identicon"])
    hash = hashlib.md5()
    hash.update("{}".format(email.lower()).encode('utf-8'))
    email_hash = hash.hexdigest()
    img = "https://secure.gravatar.com/avatar/d={}?{}.jpg".format(default, email_hash)
    img_path = os.path.join(settings.MEDIA_ROOT, 'avatar/')
    img_file = img_path + '%s.jpg'%(email_hash)
    if not os.path.exists(img_file):
        response = requests.get(img)
        image = Image.open(BytesIO(response.content))
        image.save(img_file)
    return '/media/avatar/{}.jpg'.format(email_hash)


# return an image tag with the gravatar
# TEMPLATE USE:  {{ email|gravatar:150 }}
@register.filter
def gravatar(email, parse='40,3'):
    try:
        size, mr = parse.split(',')
    except:
        size = parse
        mr = 3
    size=int(size)
    mr=int(mr)
    url = gravatar_url(email, size)
    return mark_safe('<img src="%s" class="mr-%d img-fluid rounded-circle" height="%d" width="%d">' % (url, mr, size, size))

@register.simple_tag
def get_option(key):
    try:
        option = Option.objects.filter(key=key).order_by('-pk')
    except:
        pass
    if option.exists():
        return option.first().value
    return


@register.simple_tag
def get_links():
    try:
        links = Link.objects.filter()
    except:
        pass
    if links.exists():
        return links
    return

@register.inclusion_tag('sitemeta.html')
def sitemeta():
    from docspace.models import Taxonomy
    metadata = Taxonomy.objects.filter(mark__in=['tag', 'category']).order_by('?')
    return {'metadata': metadata}
