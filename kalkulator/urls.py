from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('kalkulator/', views.calculator, name='calculator'),
    path('kalkulator/mentes/', views.save_estimate, name='save_estimate'),
]
