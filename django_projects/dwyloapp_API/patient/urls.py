from django.contrib import admin
from django.conf.urls import url,include
from patient import views as patient_view


urlpatterns = [
url(r'^patient_register/$',patient_view.PatientRegister.as_view()),
]