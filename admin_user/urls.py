from django.contrib import admin
from django.urls import path, include
from admin_user import views as admin_view


urlpatterns = [
    path('register',admin_view.AdminRegister.as_view()),
]