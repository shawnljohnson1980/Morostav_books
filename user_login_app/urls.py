from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('morostav/dashboard', views.dashboard, name='dashboard'),  # Home/dashboard
    path('log_in/', views.login, name='log_in'),          # Login
    path('new_user/', views.user_create, name='new_user'),  # Registration
    path('logout/', views.log_out, name='logout'),
    path('login/', views.log_in, name="login"),
    path('to_login', views.to_login, name="to_login"),
    path('register/', views.register, name="register"),
    path('reset_start/', auth_views.PasswordResetView.as_view(template_name='reset_start.html'), name='password_reset_start'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='reset_done.html'), name='password_reset_complete'),
]
