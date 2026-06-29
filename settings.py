from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('properties/', views.property_list, name='property_list'),
    path('properties/add/', views.property_add, name='property_add'),
    path('properties/<int:pk>/', views.property_detail, name='property_detail'),
    path('properties/<int:pk>/edit/', views.property_edit, name='property_edit'),
    path('properties/<int:pk>/delete/', views.property_delete, name='property_delete'),
    path('deals/', views.deal_list, name='deal_list'),
    path('deals/add/', views.deal_add, name='deal_add'),
    path('deals/<int:pk>/share/', views.deal_share, name='deal_share'),
    path('finance/', views.finance, name='finance'),
    path('finance/add/', views.finance_add, name='finance_add'),
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/add/', views.task_add, name='task_add'),
    path('tasks/<int:pk>/complete/', views.task_complete, name='task_complete'),
    path('tasks/<int:pk>/archive/', views.task_archive, name='task_archive'),
    path('tasks/<int:pk>/delete/', views.task_delete, name='task_delete'),
    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.user_add, name='user_add'),
    path('external-marketers/', views.external_marketer_list, name='external_marketer_list'),
    path('external-marketers/add/', views.external_marketer_add, name='external_marketer_add'),
]
