__author__ = 'oidin'
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^getTreeData', 'webvepp.views.loadTreeData', name="views-tree-data"),
    url(r'^getTreeSample', 'webvepp.views.loadTreeSample', name="views-tree-sample"),
    url(r'^getNodeNeighbours', 'webvepp.views.loadNodeNeighbours', name="views-node-data"),
]