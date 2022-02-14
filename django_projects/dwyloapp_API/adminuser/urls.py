from django.contrib import admin
from django.conf.urls import url,include
from adminuser import views as admin_view


urlpatterns = [
 url(r'^admin_register/$',admin_view.AdminRegister.as_view()),
 ]