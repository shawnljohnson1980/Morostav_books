from django.urls import path
from django.contrib.auth import views as auth_views
from user_login_app import views as user_views
from . import views

urlpatterns = [
    # Admin Routes
    path('morostav/dashboard/', views.dashboard, name='dashboard'), 
    path('ban-ip/', views.ban_ip, name='ban_ip'),

    # 🔹 LOGIN, LOGOUT & REGISTRATION ROUTES
    path('log_in/', views.log_in, name='log_in'),         
    path('logout/', views.log_out, name='logout'),        
    path('register/', views.register, name='register'),
    path('new_user/', views.user_create, name='new_user'),

    # 🔹 PASSWORD RESET ROUTES
    path('reset/', auth_views.PasswordResetView.as_view(template_name='reset_start.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_complete'),

    # 🔹 LOGIN PAGE REDIRECT
    path('to_login/', views.to_login, name='to_login'),

    # 🔹 EMAIL VERIFICATION
    path("send_verification_email/<uidb64>/<token>/", user_views.send_verification_email, name="send_verification_email"),
    path("verify_email/<uidb64>/<token>/", views.verify_email, name="verify_email"),
]

