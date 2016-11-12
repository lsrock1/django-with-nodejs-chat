from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^master/$', views.master, name='master'),
    url(r'^ajax/$',views.ajax_api),
    # url(r'^node_api$', 'core.views.node_api', name='node_api'),
]