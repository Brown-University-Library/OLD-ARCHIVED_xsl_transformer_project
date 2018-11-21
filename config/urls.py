# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import RedirectView
from transformer_app import views

admin.autodiscover()


urlpatterns = [

    url( r'^admin/', admin.site.urls ),

    url( r'^v1/$', views.run_transform_v1, name='transformer_v1_url' ),
    url( r'^v1/shib/$', views.run_transform_v1, name='transformer_v1_url' ),

    url( r'^keymaker/$', views.keymaker, name='keymaker_url' ),

    url( r'^info/$', views.info, name='info_url' ),

    url( r'^$', RedirectView.as_view(pattern_name='info_url') ),

    ]
