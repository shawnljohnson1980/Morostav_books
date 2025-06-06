from django.db import models
from django import forms
from django.conf import settings
from django_starfield import Stars
from datetime import datetime
from django.db.models import Avg
from user_login_app.models import User,BlockedIP
from django.contrib import admin

# 🚀 Genre Model
class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class BookManager(models.Manager):
    def create_validated(self, title, description, cover_image, genre, isbn, published_date):
        if not title:
            raise ValueError('Title is required.')
        if len(title) < 3:
            raise ValueError('Title must be at least 3 characters long.')
        if self.model.objects.filter(title=title).exists():
            raise ValueError("Title is already in use.")
        if not description:
            raise ValueError("Description is required.")
        if len(description) < 10 or len(description) > 300:
            raise ValueError("Description must be between 10 and 300 characters.")
        if not genre:
            raise ValueError("Genre is required.")
        if not isbn:
            raise ValueError("ISBN is required.")
        if not cover_image:
            raise ValueError("Cover image is required.")
        if not published_date:
            raise ValueError("Publish date is required.")
        book = self.model(
            title=title.strip(),
            description=description.strip(),
            genre=genre,
            isbn=isbn,
            cover_image=cover_image,
            published_date=published_date,
        )
        book.save(using=self._db)
        return book
class Book(models.Model):
    title = models.CharField(max_length=65)
    description = models.TextField(max_length=400)
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    genre = models.ForeignKey('Genre', on_delete=models.SET_NULL, null=True)
    isbn = models.CharField(max_length=13, unique=True, blank=True, null=True)
    published_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = BookManager()
    def average_rating(self):
        avg = self.ratings.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0
    def __str__(self):
        return self.title
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

class Rating(models.Model):
    book = models.ForeignKey(Book, related_name="ratings", on_delete=models.CASCADE)
    rating = models.IntegerField()
    review = models.TextField()
    creator = models.ForeignKey(User, related_name='user_ratings', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if "buy followers" in self.review.lower():
            request = kwargs.get('request')
            if request:
                ip = request.META.get('REMOTE_ADDR')
                if ip and not BlockedIP.objects.filter(ip_address=ip).exists():
                    BlockedIP.objects.create(ip_address=ip)
                    print(f"🔥 IP {ip} blocked for spam.")

    def __str__(self):
        return f"{self.creator.username} - {self.rating}⭐"

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating', 'review']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, f"{i}⭐") for i in range(1, 6)], attrs={"class": "star-rating"}),
            'review': forms.Textarea(attrs={"class": "review-box", "rows": 4, "placeholder": "Write your review..."}),
        }
class ReviewReply(models.Model):
    rating = models.OneToOneField(Rating, related_name='reply', on_delete=models.CASCADE)
    responder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply by {self.responder.username} to {self.rating.creator.username}'s review"
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

