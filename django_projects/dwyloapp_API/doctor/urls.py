from django.contrib import admin
from django.urls import path,include
from doctor import views as doctor_view




urlpatterns = [
    path('register',doctor_view.DoctorRegister.as_view()),
    path('profile-update',doctor_view.DoctorProfileView.as_view()),
    path('set-availability',doctor_view.DoctorAvailabilitySet.as_view()),
    path('all-review',doctor_view.DoctorAllReview.as_view()),
    path('consultation-detail/<uuid:id>/',doctor_view.ConsultationDetailView.as_view()),
  ]