__author__ = 'oidin'
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^getTreeData', 'webvepp.views.getTreeData', name="views-tree-data"),
]