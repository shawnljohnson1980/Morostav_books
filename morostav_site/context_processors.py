
def timestamp_context(request):  # Check for typos in the function name
    from datetime import datetime
    return {'timestamp': datetime.now()}

'morostav_site.context_processors.timestamp_context'  # ✅ This is key
from time import time
from .models import Book
from django.db.models import Avg

def general_context(request):
    books = Book.objects.all()
    for book in books:
        book.avg_rating = book.ratings.aggregate(Avg('rating'))['rating__avg'] or 0
        book.latest_reviews = book.ratings.all().order_by('-created_at')[:3]
    
    return {
        'timestamp': int(time()),
        'books': books,  # 👈 This is the key test injection
    }
