# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible, force_text
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property
from django.dispatch import receiver

TABLE_PREFIX = getattr(settings, "DS_TABLE_PREFIX", "ds")

# Create your models here.

class Created(models.Model):
    created = models.DateTimeField(
        editable=True,
        verbose_name=u"创建日期",
        default=timezone.datetime.now,
        )
    class Meta:
        abstract = True


class Modified(models.Model):
    modified = models.DateTimeField(
        auto_now=True,
        verbose_name=u"修改日期",
        )
    class Meta:
        abstract = True


class Parent(models.Model):
    parent = models.ForeignKey(
        'self',
        blank=True, null=True,
        verbose_name=u"父级ID",
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_parent",
        )

    class Meta:
        abstract = True


class SlugAble(models.Model):
    slug = models.SlugField(
        max_length=200,
        blank=True,
        null=True,
        )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        from django.utils.http import urlquote
        from django.utils.text import slugify
        if not self.slug:
            if hasattr(self, 'title'):
                slug = self.title
            elif hasattr(self, 'key'):
                slug = self.key
            self.slug = urlquote(slugify(slug, allow_unicode=True))
        return super(SlugAble, self).save(*args, **kwargs)


@python_2_unicode_compatible
class BaseMetaData(models.Model):
    key = models.CharField(max_length=64, verbose_name=u"键名")
    value = models.TextField(verbose_name=u"键值")

    def __str__(self):
        return "{%s: %s}" %(self.key, self.value)

    class Meta:
        abstract = True


@python_2_unicode_compatible
class Metadata(BaseMetaData):
    content_type = models.ForeignKey(
        ContentType,
        models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_('content type'),
        related_name="%(app_label)s_%(class)s_content_type")
    object_id = models.PositiveIntegerField(_('object id'), blank=True, null=True)
    object_repr = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return force_text(self.object_repr)

    class Meta:
        db_table = '%s_metadatas' % TABLE_PREFIX
        verbose_name = verbose_name_plural =u"元数据"


@python_2_unicode_compatible
class Option(BaseMetaData):
    autoload = models.BooleanField(default=False, verbose_name=u"自动加载")

    class Meta:
        db_table = '%s_options' % TABLE_PREFIX
        verbose_name = verbose_name_plural =u"选项"


@python_2_unicode_compatible
class Taxonomy(BaseMetaData, Parent):
    TAXONOMY_MARK = (
        ('tag', u"标签"),
        ('category', u"分类"),
        ('link', u"链接"),
        ('file', u"文件"),
        ('photo', u"图像"),
        ('audio', u"音频"),
        ('video', u"视频"),
        ('special', u"专题"),
        )
    mark = models.SlugField(
        max_length=12,
        default='tag',
        choices=TAXONOMY_MARK,
        verbose_name=u"标记",
        )
    description = models.TextField(
        null=True, blank=True,
        verbose_name=u"描述")

    def __str__(self):
        return self.key

    @property
    def related_count(self):
        if self.mark == 'tag':
            return self.docspace_article_tags.filter(status='published').count()
        elif self.mark == 'category':
            return self.docspace_article_category.filter(status='published').count()
        else:
            return 0

    class Meta:
        db_table = '%s_taxonomys' % TABLE_PREFIX
        verbose_name = verbose_name_plural =u"分类"

class User(AbstractUser):
    nickname = models.CharField(
        max_length=64,
        blank=True,
        verbose_name = u"用户昵称",
        )
    mobile = models.CharField(
        max_length=16,
        blank=True,
        verbose_name=u"手机号码",
        )
    website = models.URLField(
        blank=True,
        null=True,
        verbose_name=u"个人站点"
        )
    role = models.SlugField(
        default='editor',
        verbose_name=u"用户角色",
        )
    resume = models.TextField(
        blank=True,
        null=True,
        verbose_name=u"个人简介",
        )

    def __str__(self):
        return self.nickname or self.username

    @cached_property
    def nature_name(self):
        return self.nickname or self.username

    @cached_property
    def website_url(self):
        if self.website:
            return self.website
        else:
            return ''

    class Meta(AbstractUser.Meta):
        db_table = '%s_users' % TABLE_PREFIX


class Link(models.Model):
    name = models.CharField(max_length=255, verbose_name=u"名称", db_column='link_name')
    url = models.URLField(max_length=255, verbose_name=u"Web地址", db_column='link_url')
    image = models.CharField(max_length=255, verbose_name=u"图像地址", null=True, blank=True, db_column='link_image')
    target = models.CharField(max_length=25, verbose_name=u"打开方式", default='_blank', db_column='link_target')
    description = models.CharField(max_length=255, verbose_name=u"链接描述", null=True, blank=True, db_column='link_description')
    visible = models.CharField(max_length=20, null=True, blank=True, db_column='link_visible')
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,  related_name='links', db_column='link_owner')
    rating = models.IntegerField(default=0, verbose_name=u"评分", db_column='link_rating')
    updated = models.DateTimeField(blank=True, null=True, db_column='link_updated')
    rel = models.CharField(max_length=255, verbose_name=u"链接关系(XFN)", default='friend', db_column='link_rel')
    notes = models.TextField(verbose_name=u"备注", null=True, blank=True, db_column='link_notes')
    rss = models.CharField(max_length=255, verbose_name=u"RSS地址", null=True, blank=True, db_column='link_rss')

    class Meta:
        db_table = '%s_links' % TABLE_PREFIX
        verbose_name = verbose_name_plural =u"链接"

    def __str__(self):
        return "%s %s" % (self.name, self.url)

    def is_visible(self):
        return self.visible == 'Y'


class ArticleManager(models.Manager):

    def get_queryset(self):
        return super(ArticleManager, self).get_queryset().filter(post_type__in=['post', 'page'])


from simditor.fields import RichTextField
@python_2_unicode_compatible
class Article(Created, Modified, Parent):
    """docstring for Article."""
    ARTICLE_STATUS = (
        ('draft', u"草稿"),
        ('trash', u"已回收"),
        ('published', u"已发布"),
        ('pending', u"等待复审"),
        ('inherit', u"继承"),
        ('auto-draft', u"自动保存"),
        )
    POST_TYPE = (
        ('post', u"文章"),
        ('page', u"页面"),
        ('attachment', u"附件"),
        )
    COMMENT_STATUS = (
        ('open', u"开放"),
        ('closed', u"关闭"),
        )
    title = models.CharField(
        max_length=128,
        verbose_name=u"标题",
        )
    #content = RichTextField(
    content = models.TextField(
        null=True,
        blank=True,
        verbose_name=u"内容",
        )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        verbose_name=u"作者",
        on_delete=models.SET_NULL
        )
    comment_status = models.SlugField(
        default='open',
        choices=COMMENT_STATUS,
        verbose_name=u"会话状态",
        )
    mime_type = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name=u"MIME类型",
        )
    post_type = models.SlugField(
        max_length=64,
        default='post',
        choices=POST_TYPE,
        verbose_name=u"文章类型",
        )
    status = models.SlugField(
        default='auto-draft',
        verbose_name=u"状态",
        choices=ARTICLE_STATUS,
        )
    category = models.ManyToManyField(
        'Taxonomy',
        blank=True,
        verbose_name=u"分类",
        limit_choices_to={'mark': 'category'},
        related_name="%(app_label)s_%(class)s_category",
        )
    tags = models.ManyToManyField(
        'Taxonomy',
        blank=True,
        verbose_name=u"标签",
        limit_choices_to={'mark': 'tag'},
        related_name="%(app_label)s_%(class)s_tags",
        )
    views_num = models.PositiveIntegerField(default=0, verbose_name=u"阅读数")
    comment_num = models.PositiveIntegerField(default=0, verbose_name=u"评论数")
    objects = ArticleManager()

    def __str__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('detail', [self.pk])

    def get_comments(self):
        return self.docspace_comment_article.filter(
            approved='yes', parent_id=None).order_by('-created')

    def comment_count(self):
        return self.docspace_comment_article.filter(approved='yes').count()

    def related_articles(self):
        related_articles = self._meta.model.objects.exclude(
            pk=self.pk).filter(models.Q(tags__in=self.tags.all()))
        return related_articles

    class Meta:
        db_table = '%s_articles' % TABLE_PREFIX
        verbose_name = verbose_name_plural = u"文章"


class MediaManager(models.Manager):

    def get_queryset(self):
        return super(MediaManager, self).get_queryset().filter(post_type='attachment')


class Media(Article):

    objects = MediaManager()

    class Meta:
        proxy = True
        verbose_name = verbose_name_plural = u"媒体"


@python_2_unicode_compatible
class Comment(Created, Parent):
    article = models.ForeignKey(
        'Article',
        verbose_name=u"所属文章",
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_article",
        )
    author_name = models.CharField(
        max_length=12,
        verbose_name=u"姓名",
        )
    author_email = models.EmailField(
        max_length=36,
        verbose_name=u"电子邮件",
        )
    author_url = models.URLField(
        blank=True,
        null=True,
        verbose_name=u"站点",
        )
    author_ip = models.GenericIPAddressField(
        verbose_name=u"IP地址",
    )
    content = models.TextField(
        verbose_name=u"评论内容",
        )
    approved = models.SlugField(
        default='yes',# choices in [spam, yes, no,]
        verbose_name=u"是否被批准",
        )
    agent = models.TextField(
        null=True, blank=True,
        verbose_name="Agent",
        )
    notify = models.SlugField(
        default='push',
        verbose_name=u"通知",
        )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        verbose_name=u"用户",
        on_delete=models.SET_NULL
        )

    def __str__(self):
        return force_text(self.article)

    def children(self):
        obj = self._meta.model.objects.filter(approved='yes', parent_id=self.pk)
        return obj

    class Meta:
        db_table = '%s_comments' % TABLE_PREFIX
        verbose_name = verbose_name_plural = u"评论"

@receiver(models.signals.post_save, sender=Comment)
def update_article_comment_count(instance, **kwargs):
    article = instance.article
    _model = instance._meta.model
    count = _model.objects.filter(approved='yes', article=article).count()
    if article.comment_num != count:
        article.comment_num = count
        article.save()
