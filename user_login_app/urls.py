from django.urls import path
from django.contrib.auth import views as auth_views
from user_login_app import views

urlpatterns = [
    path('morostav/dashboard/', views.dashboard, name='dashboard'),  # Admin Dashboard
    path('ban-ip/', views.ban_ip, name='ban_ip'),
    # 🔹 LOGIN, LOGOUT & REGISTRATION ROUTES
    path('log_in/', views.log_in, name='log_in'),         # ✅ Form Submission Route
    path('logout/', views.log_out, name='logout'),        # ✅ Fixed Slash Consistency
    path('register/', views.user, name='register'),
    path('new_user/', views.user_create, name='new_user'),

    # 🔹 PASSWORD RESET ROUTES
    path('reset/', auth_views.PasswordResetView.as_view(template_name='reset_start.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    # 🔹 LOGIN PAGE REDIRECT
    path('to_login/', views.to_login, name='to_login'),
]