# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals
from django.conf.urls import url, include
from django.http import HttpResponse
from django.views.generic import View


class Article(View):
    def get(self, request, article_id):
        return HttpResponse("article:%(article_id)s" % {
            'article_id': article_id,
    })


def comment_with_article(request, article_id, comment_id):
    return HttpResponse("article:%(article_id)s, comment:%(comment_id)s" % {
            'article_id': article_id,
            'comment_id': comment_id,
    })


def comment_without_article(request, comment_id):
    return HttpResponse("article:%(article_id)s, comment:%(comment_id)s" % {
            'article_id': None,
            'comment_id': comment_id,
    })


comment_with_article_url = url(
    regex=r'^(?P<article_id>\d+)/comment_with_article/(?P<comment_id>\d+)/$',
    view=comment_with_article,
    name='comment_with_article'
)

comment_without_article_url = url(
    regex=r'^(?P<article_id>\d+)/comment_without_article/(?P<comment_id>\d+)/$',
    view=comment_without_article,
    name='comment_without_article',
)


article_url = url(
    regex=r'^(?P<article_id>\d+)/$',
    view=Article.as_view(),
    name='article_detail'
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
