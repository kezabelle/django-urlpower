# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals
# from django.conf.urls import url, include
import json
from django.http import HttpResponse
from django.utils import six
from django.views.generic import View
from urlpower import url, include, to_int
from django.conf.urls import url as django_url


class Article(View):
    def get(self, request, article_id):
        vals = locals(); vals.pop('request'); vals.pop('self')
        return HttpResponse(json.dumps(vals))


def comment_with_article(request, article_id, comment_id, *args, **kwargs):
    vals = locals(); vals.pop('request')
    return HttpResponse(json.dumps(vals))


def comment_without_article(request, comment_id):
    vals = locals(); vals.pop('request')
    return HttpResponse(json.dumps(vals))


comment_with_article_url = url(
    regex=r'^(?P<article_id>\d+)/comment_with_article/(?P<comment_id>\d+)/$',
    view=comment_with_article,
    name='comment_with_article',
    kwargs={'lol': 1},
    # unnamed_args=,
    named_args={0:[to_int], 'comment_id': to_int}
)

comment_without_article_url = url(
    regex=r'^([1-9]+)/comment_without_article/(?P<comment_id>\d+)/$',
    view=comment_without_article,
    name='comment_without_article',
    # unnamed_args=[to_int],
    named_args={0: to_int, 'comment_id': to_int},
    # ignores=[0],
)


article_url = url(
    regex=r'^(\d+)/$',
    view=Article.as_view(),
    name='article_detail',
    # unnamed_args=[to_int],
    named_args={0: to_int},
)

more_urlpatterns = [
    comment_with_article_url,
    comment_without_article_url,
    article_url,
]

urlpatterns = [
    url(r'^included/', include(more_urlpatterns)),
    comment_with_article_url,
    comment_without_article_url,
    article_url,
    # url(r'^', include(admin.site.urls)),
]
