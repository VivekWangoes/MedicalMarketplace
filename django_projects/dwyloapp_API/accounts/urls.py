from django.contrib import admin
from django.urls import path,include
from accounts import views as account_view

app_name = "accounts"
urlpatterns = [
	path('user',account_view.Users.as_view()),
    path('verify-email',account_view.VerifyEmail.as_view()),
    path('resend-otp',account_view.VerifyEmail.as_view()),
    path('send-otp',account_view.VerifyEmail.as_view()),
    path('loginwith-otp',account_view.LoginWithOTP.as_view()),
    path('signin',account_view.SignIn.as_view()),
    path('logout',account_view.UserLogout.as_view()),
    path('contact-support-view',account_view.ContactSupportQueryView.as_view()),
    path('contact-support-query',account_view.ContactSupportQueryRegistered.as_view()),
    path('forgot-password' ,account_view.ForgotPassword.as_view() , name="forgot_password"),
    path('change-password/<uidb64>/<token>/' , account_view.change_password , name="change_password"),
  ]