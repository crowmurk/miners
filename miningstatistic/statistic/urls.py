from django.urls import path, include

from . import views


app_name = 'statistic'

server = [
    path('', views.ServerStatisticList.as_view(), name='list'),
]

urlpatterns = [
    path('server/', include((server, 'server')))
]
