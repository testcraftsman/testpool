"""djconfig URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import RedirectView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from testpooldb import views
import profile

urlpatterns = patterns("",
    url(r'^testpool/admin/', include(admin.site.urls)),
    url(r'^testpool/profile/', include("profile.urls")),
    url(r'^testpool/api/profiles', views.profile_list),
    url(r'^testpool/api/profiles/(?P<pk>[0-9]+/$)', views.profile_detail),
)

urlpatterns += staticfiles_urlpatterns()
