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
	path('complete-profile',patient_view.PatientCompleteProfile.as_view()),

	path('search-by-speciality',patient_view.DoctorSearchBySpecialty.as_view()),
    path('search-by-clinic',patient_view.DoctorSearchByClinic.as_view()),
    path('search-by-healthconcern',patient_view.DoctorSearchByHealthConcern.as_view()),
    path('search-by-doctors',patient_view.DoctorSearchByDoctors.as_view()),
    path('availability-profile',patient_view.DoctorAvailabilityProfile.as_view()),
    path('availability-timeslot',patient_view.DoctorAvailabilityTimeSlot.as_view()),
    path('confirm-appointment',patient_view.ConfirmAppointmentsView.as_view()),
    path('upcoming-appointment',patient_view.UpcomingAppointments.as_view()),
    path('completed-appointment',patient_view.CompletedAppointments.as_view()),
    path('cancle-appointment/<uuid:id>/',patient_view.CancleAppointment.as_view()),
    path('write-review',patient_view.DoctorReviewView.as_view()),
	path('consultation-detail/<uuid:id>/',patient_view.PatientConsultationDetail.as_view()),

	path('address',patient_view.AddressView.as_view()),
	path('medicine',patient_view.MedicineView.as_view()),
	path('item-addtocart',patient_view.MyCartItemView.as_view())
	]