from . import views
from django.urls import path
from django.urls import include

urlpatterns = [
    path('', views.startPage, name='startpage'),
    path('about/', views.aboutPage, name='aboutpage'),
    path('subscription/', views.subscriptionPage, name='subscriptionpage'),
    path('grouptag/login', views.loginPage, name='logingrouptag'),
    path('grouptag/logout', views.logoutPage, name='logoutgrouptag'),
    path('grouptag/dashboard', views.dashboardPage, name='dashboard'),
    path('grouptag/usuarios', include('users.urls'), name='usuarios'),
    path('grouptag/horarios', include('schedules.urls'), name='horarios'),
]  
