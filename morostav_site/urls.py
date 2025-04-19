from django.urls import path
from . import views
from .views import dashboard


urlpatterns = [
    path('', views.index, name="home"),
    path('books/<int:book_id>/', views.book, name='book'),
    path('gallery',views.gallery, name="gallery"),
    path('reviews', views.add_review, name="reviews"),
    path('about', views.about,name="about"),
    path('books_home', views.books_home, name="books_home"),
    path('add_book', views.add_book, name="add_book"),
    path('calendar/', views.calendar_view, name='calendar'),  # Users can see it
    path('calendar/events/', views.get_events, name='get_calendar_events'),  # Fetch events dynamically
    path('calendar/add_event/', views.add_event, name='add_event'),  # Admin-only route
    path('books/<int:book_id>/review/edit/', views.edit_review, name='edit_review'),
    path('reviews/<int:review_id>/reply/', views.reply_to_review, name='reply_to_review'),
    path('new_review', views.new_review, name="new_review"),
    path('contact', views.contact, name='contact'), 
]
