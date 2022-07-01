from django.contrib import admin
from django.urls import path,include
from accounts import views as account_view

app_name = "accounts"
urlpatterns = [
	path('user',account_view.UsersView.as_view()),
    path('verify-email',account_view.VerifyEmail.as_view()),
    path('resend-emailverify-otp',account_view.VerifyEmail.as_view()),
    path('resend-login-otp',account_view.LoginWithOTP.as_view()),
    path('loginwith-otp',account_view.LoginWithOTP.as_view()),
    path('signin',account_view.SignIn.as_view()),
    path('logout',account_view.UserLogout.as_view()),
    path('contact-support-view',account_view.ContactSupportQueryView.as_view()),
    path('contact-support-query',account_view.ContactSupportQueryRegister.as_view()),
    path('forgot-password' ,account_view.ForgotPassword.as_view() , name="forgot_password"),
    path('change-password/<uidb64>/<token>/' , account_view.change_password , name="change_password"),

    path('google-token', account_view.GoogleTokenGenerate.as_view(), name="google_token"),
  ]