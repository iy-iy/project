from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('income/', views.income_view, name='income'),
    path('chart/', views.generate_chart, name='generate_chart'),
]
