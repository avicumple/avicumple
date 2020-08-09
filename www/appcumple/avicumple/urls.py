from django.conf.urls import patterns,url
from avicumple import views, views_mocked

from django.conf import settings


if settings.MOCK_FACEBOOK_SERVICES:
	print(settings.MOCK_FACEBOOK_SERVICES)
	urlpatterns = patterns('', url(r'^$', views_mocked.login, name='login'),
		url(r'^register/$', views_mocked.register, name='register'),
		url(r'^list/$', views_mocked.list, name='list'),
		url(r'^(?P<id_fb>\d+)/$',views_mocked.detail,name='detail'),
		)
else:
	urlpatterns = patterns('', url(r'^$', views.login, name='login'),
		url(r'^register/$', views.register, name='register'),
		url(r'^list/$', views.list, name='list'),
		url(r'^(?P<id_fb>\d+)/$', views.detail, name='detail'),
		)