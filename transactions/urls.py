from django.urls import path
from . import views

urlpatterns = [
    path('', views.transaction_list, name='transaction_list'),
    path('dashboard/', views.dashboard, name='dashboard'),
]