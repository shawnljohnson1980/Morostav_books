from django.db import models
from django import forms
from django.conf import settings
from django_starfield import Stars
from datetime import datetime
from django.db.models import Avg
from user_login_app.models import User
from django.contrib import admin

# 🚀 Genre Model
class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

# 📚 Book Model
class Book(models.Model):
    title = models.CharField(max_length=65)
    description = models.TextField(max_length=400)
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True)
    isbn = models.CharField(max_length=13, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def average_rating(self):
        """Calculate and return the average rating for this book."""
        avg = self.ratings.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0

    def __str__(self):
        return self.title


# ⭐ Rating Manager (Handles Review Validation)
class RatingManager(models.Manager):
    def validator(self, post_data):
        errors = {}

        review = post_data.get('review', '').strip()
        rating = post_data.get('rating')

        if len(review) < 10 or len(review) > 400:
            errors['review_length'] = "Reviews must be between 10 and 400 characters."

        if rating and not (1 <= int(rating) <= 5):
            errors['rating_range'] = "Rating must be between 1 and 5."

        return errors


# ⭐ Rating Model (Users Leave Reviews on Books)
class Rating(models.Model):
    book = models.ForeignKey(Book, related_name="ratings", on_delete=models.CASCADE)  # ✅ Fix: `related_name="ratings"`
    rating = models.IntegerField()
    review = models.TextField()
    creator = models.ForeignKey(User, related_name='user_ratings', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = RatingManager()

    def __str__(self):
        return f"{self.creator.username} - {self.rating}⭐"


# ✨ Form for submitting book ratings
class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating', 'review']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, f"{i}⭐") for i in range(1, 6)], attrs={"class": "star-rating"}),
            'review': forms.Textarea(attrs={"class": "review-box", "rows": 4, "placeholder": "Write your review..."}),
        }


class GalleryImage(models.Model):  # ✅ Ensured class declaration is complete
    title = models.CharField(max_length=100, unique=True)
    thumbnail = models.ImageField(upload_to='gallery/thumbnails/')
    full_size = models.ImageField(upload_to='gallery/fullsize/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title



class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} ({self.start_time.strftime('%Y-%m-%d %H:%M')})"

class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "start_time", "end_time", "created_by")
    list_filter = ("start_time", "created_by")