from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/signup/', views.signup, name='signup'),
    path('farmer/', views.farmer_dashboard, name='farmer_dashboard'),
    path('marketplace/', views.marketplace, name='marketplace'),
]
