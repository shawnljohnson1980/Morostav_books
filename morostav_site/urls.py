from django.urls import path
from .views import dashboard
from . import views

urlpatterns = [
    path('', views.home, name= "home"),
    path('dashboard/', dashboard, name='dashboard'),
#   path('contact/', views.get_contacts, name='contact'),
#  path('contact/get_contacts', views.get_contacts, name="get contacts"),
    #path('contact/process', views.process, name= 'process'),
#  path('contact/get_calendar', views.fetch_calendar_events, name= "get calender"),
]
