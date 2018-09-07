__author__ = 'oidin'
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^camacs/$', 'webvepp.views.camacs', name="index-camacs"),
    url(r'^camacs/(?P<id>[-@\w]+)$', 'webvepp.views.camacs', name="index-camacs"),
    url(r'^elements/$', 'webvepp.views.elements', name="index-elements"),
    url(r'^elements/(?P<id>[-@\w]+)$', 'webvepp.views.elements', name="index-elements"),
    url(r'^scheme/$', 'webvepp.views.scheme', name="index-scheme"),
    url(r'^scheme/[- \w]+$', 'webvepp.views.scheme', name="index-scheme"),
    url(r'^tools/$', 'webvepp.views.tools', name="index-tools"),
    url(r'^settings/$', 'webvepp.views.settings', name="index-settings"),
    url(r'^findObject', 'webvepp.views.findObject', name="find-object"),
    url(r'^getTreeData', 'webvepp.views.loadTreeData', name="views-tree-data"),
    url(r'^getListData', 'webvepp.views.loadListData', name="views-list-data"),
    url(r'^getMenuData', 'webvepp.views.loadMenuData', name="views-menu-data"),
    url(r'^getToolData', 'webvepp.views.loadToolData', name="views-tool-data"),
    url(r'^getTreeSample', 'webvepp.views.loadTreeSample', name="views-tree-sample"),
    url(r'^getValidationData', 'webvepp.views.loadValidationData', name="views-validation-data"),
    url(r'^getNodeNeighbours', 'webvepp.views.loadNodeNeighbours', name="views-node-data"),
    url(r'^getMaxAttributes', 'webvepp.views.loadMaxAttributes', name="views-max-data"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL , document_root = settings.STATIC_ROOT )