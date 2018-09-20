from django.urls import path, include

from . import views


app_name = 'miner'

request = [
    path('create/', views.RequestCreate.as_view(), name='create'),
    path('<slug:request_slug>/',
         views.RequestDetail.as_view(), name='detail'),
    path('<slug:request_slug>/update/',
         views.RequestUpdate.as_view(), name='update'),
    path('<slug:request_slug>/delete/',
         views.RequestDelete.as_view(), name='delete'),
]

miner = [
    path('', views.MinerList.as_view(), name='list'),
    path('create/', views.MinerCreate.as_view(), name='create'),
    path('<slug:slug>/', views.MinerDetail.as_view(), name='detail'),
    path('<slug:miner_slug>/', include((request, 'request'))),
    path('<slug:slug>/update/', views.MinerUpdate.as_view(), name='update'),
    path('<slug:slug>/delete/', views.MinerDelete.as_view(), name='delete'),
]

server = [
    path('', views.ServerList.as_view(), name='list'),
    path('create/', views.ServerCreate.as_view(), name='create'),
    path('<slug:slug>/', views.ServerDetail.as_view(), name='detail'),
    path('<slug:slug>/update/', views.ServerUpdate.as_view(), name='update'),
    path('<slug:slug>/delete/', views.ServerDelete.as_view(), name='delete'),
]

urlpatterns = [
    path('miner/', include((miner, 'miner'))),
    path('server/', include((server, 'server'))),
]
