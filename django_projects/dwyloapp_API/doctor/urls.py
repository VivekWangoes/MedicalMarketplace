from django.contrib import admin
from django.urls import path,include
from doctor import views as doctor_view




urlpatterns = [
    path('register',doctor_view.DoctorRegister.as_view()),
    #path('doctor-profile-register',doctor_view.DoctorProfileRegister.as_view()),
    path('profile-update',doctor_view.DoctorProfileUpdate.as_view()),
    path('info',doctor_view.DoctorInfoView.as_view()),
    path('search-by-speciality',doctor_view.DoctorSearchBySpecialty.as_view()),
    path('search-by-clinic',doctor_view.DoctorSearchByClinic.as_view()),
    path('search-by-healthconcern',doctor_view.DoctorSearchByHealthConcern.as_view()),
    path('search-by-doctors',doctor_view.DoctorSearchByDoctors.as_view()),
    path('set-availability',doctor_view.DoctorAvailabilityView.as_view()),

  ]