from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Book, Rating, Genre

# Inline model for managing reviews inside book admin
class RatingInline(admin.TabularInline):
    model = Rating
    extra = 1  # Allows adding reviews within the book admin page

# Admin for Genres
@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# Admin for Books
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'isbn', 'genre', 'display_average_rating', 'created_at')
    list_filter = ('genre',)  # Adds filtering by genre
    search_fields = ('title', 'isbn')
    inlines = [RatingInline]  # Enables inline review editing

    def display_average_rating(self, obj):
        """Calculate and display average rating in admin"""
        avg_rating = obj.rating.aggregate_avg('rating')
        return f"{avg_rating:.1f} / 5" if avg_rating else "No ratings"
    
    display_average_rating.short_description = "Avg Rating"

# Admin for Reviews
@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('creator', 'book', 'rating', 'created_at')
    list_filter = ('rating',)  # Filter reviews by star rating
    search_fields = ('creator__username', 'book__title')
