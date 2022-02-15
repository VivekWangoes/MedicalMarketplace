from django.contrib import admin
from django.urls import path, include
from patient import views as patient_view


urlpatterns = [
	path('register',patient_view.PatientRegister.as_view()),
	]