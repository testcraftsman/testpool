from django.conf.urls import patterns, url
from . import views 
urlpatterns = patterns(
  "profile",
  url(r"^$", views.index),
)
