from django.urls import path, include

from . import views


app_name = 'task'

config = [
    path('', views.ConfigList.as_view(), name='list'),
    path('create/', views.ConfigCreate.as_view(), name='create'),
    path('<slug:slug>/', views.ConfigDetail.as_view(), name='detail'),
    path('<slug:slug>/update/', views.ConfigUpdate.as_view(), name='update'),
    path('<slug:slug>/delete/', views.ConfigDelete.as_view(), name='delete'),
]

servertask = [
    path('', views.ServerTaskList.as_view(), name='list'),
    path('create/', views.ServerTaskCreate.as_view(), name='create'),
    path('<int:pk>/', views.ServerTaskDetail.as_view(), name='detail'),
    path('<int:pk>/update/', views.ServerTaskUpdate.as_view(), name='update'),
    path('<int:pk>/delete/', views.ServerTaskDelete.as_view(), name='delete'),
]

statistic = [
    path('', views.server_statistic, name='server'),
]

urlpatterns = [
    path('config/', include((config, 'config'))),
    path('task/', include((servertask, 'servertask'))),
    path('statistic/', include((statistic, 'statistic')))
]
