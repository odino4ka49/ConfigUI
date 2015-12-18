__author__ = 'oidin'
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^camacs/$', 'webvepp.views.camacs', name="index-camacs"),
    url(r'^camacs/(?P<id>\w+)$', 'webvepp.views.camacs', name="index-camacs"),
    url(r'^elements/$', 'webvepp.views.elements', name="index-elements"),
    url(r'^elements/(?P<id>\w+)$', 'webvepp.views.elements', name="index-elements"),
    url(r'^getTreeData', 'webvepp.views.loadTreeData', name="views-tree-data"),
    url(r'^getTreeSample', 'webvepp.views.loadTreeSample', name="views-tree-sample"),
    url(r'^getNodeNeighbours', 'webvepp.views.loadNodeNeighbours', name="views-node-data"),
    url(r'^getMaxAttributes', 'webvepp.views.loadMaxAttributes', name="views-max-data"),
]