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

server = [
    path('', views.ServerTaskList.as_view(), name='list'),
    path('create/', views.ServerTaskCreate.as_view(), name='create'),
    path('<int:pk>/', views.ServerTaskDetail.as_view(), name='detail'),
    path('<int:pk>/update/', views.ServerTaskUpdate.as_view(), name='update'),
    path('<int:pk>/delete/', views.ServerTaskDelete.as_view(), name='delete'),
]

urlpatterns = [
    path('config/', include((config, 'config'))),
    path('server/', include((server, 'server'))),
]
