from django.contrib import admin
from django.urls import path,include
from doctor import views as doctor_view




urlpatterns = [
    path('register',doctor_view.DoctorRegister.as_view()),
    path('profile',doctor_view.DoctorProfileView.as_view()),
    path('search-by-speciality',doctor_view.DoctorSearchBySpecialty.as_view()),
    path('search-by-clinic',doctor_view.DoctorSearchByClinic.as_view()),
    path('search-by-healthconcern',doctor_view.DoctorSearchByHealthConcern.as_view()),
    path('search-by-doctors',doctor_view.DoctorSearchByDoctors.as_view()),
    path('set-availability',doctor_view.DoctorAvailabilitySet.as_view()),
    path('availability-profile',doctor_view.DoctorAvailabilityProfile.as_view()),
    path('availability-timeslot',doctor_view.DoctorAvailabilityTimeSlot.as_view()),
    path('confirm-appointment',doctor_view.ConfirmAppointmentsView.as_view()),
    path('upcoming-appointment',doctor_view.UpcomingAppointments.as_view()),
    path('completed-appointment',doctor_view.CompletedAppointments.as_view()),
    path('cancle-appointment/<uuid:id>/',doctor_view.CancleAppointment.as_view()),
    path('write-review',doctor_view.DoctorReview.as_view()),
    
  ]