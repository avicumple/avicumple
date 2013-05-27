from django.conf.urls import patterns,url
from avicumple import views


urlpatterns = patterns('', url(r'^$', views.login, name='login'),
	url(r'^register/$', views.register, name='register'),
	url(r'^list/$', views.list, name='list'),
	url(r'^(?P<id_fb>\d+)/$',views.detail,name='detail'),
	)