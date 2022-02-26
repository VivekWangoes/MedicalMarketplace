from django.contrib import admin
from django.urls import path, include
from patient import views as patient_view


urlpatterns = [
	path('register',patient_view.PatientRegister.as_view()),
	path('alergies',patient_view.AllergyView.as_view()),
	path('medication',patient_view.MedicationView.as_view()),
	path('dieseas',patient_view.DiseaseView.as_view()),
	path('injuries',patient_view.InjuryView.as_view()),
	path('surgery',patient_view.SurgeryView.as_view()),
	path('profile',patient_view.PatientProfileView.as_view()),
	path('medical-profile',patient_view.PatientMedicalProfileView.as_view()),
	path('life-style',patient_view.PatientLifeStyleView.as_view()),
	
	]