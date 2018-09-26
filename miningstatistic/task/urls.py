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

task = [
    path('', views.ServerList.as_view(), name='list'),
    path('create/', views.ServerCreate.as_view(), name='create'),
    path('<int:pk>/', views.ServerDetail.as_view(), name='detail'),
    path('<int:pk>/update/', views.ServerUpdate.as_view(), name='update'),
    path('<int:pk>/delete/', views.ServerDelete.as_view(), name='delete'),
]

urlpatterns = [
    path('config/', include((config, 'config'))),
    path('task/', include((task, 'server'))),
]
