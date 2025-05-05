from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Avg
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.views.decorators.csrf import csrf_exempt
import json
from django.conf import settings
from .models import Book, Rating, User, GalleryImage, Genre, Event,ReviewReply
from django.views.decorators.http import require_POST
from django.conf.urls.static import static
from time import time
from .models import BlockedIP
#import logging

#logger = logging.getLogger(__name__)
# logger.info("User logged in from IP: %s", request.META.get('REMOTE_ADDR'))


def timestamp_context(request):
    return {'timestamp': int(time())}

def is_admin(user):
    return user.is_authenticated and user.is_staff

def index(request):
    latest_reviews = Rating.objects.select_related('creator', 'book').order_by('-created_at')[:3]
    featured_book = Book.objects.annotate(avg_rating=Avg('ratings__rating')).first()
    gallery_images = GalleryImage.objects.all()   
    return render(request, 'home.html', {
        'latest_reviews': latest_reviews,
        'featured_book': featured_book,
        'gallery_images': gallery_images
    })

def send_contact_form_email(first_name,last_name, email, subject, message):
    subject_line = f"New Contact Form Submission: {subject}"
    html_message = render_to_string('emails/contact_form_submission.html', {
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'subject': subject,
        'message': message,
        'protocol': 'https' if settings.USE_HTTPS else 'http',
        'domain': settings.ALLOWED_HOSTS[0],
    })
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [settings.CONTACT_EMAIL] 
    send_mail(subject_line, plain_message, from_email, to_email, html_message=html_message)

@login_required
@user_passes_test(is_admin)
def add_event(request):
    """Allows logged-in users to add an event."""
    if request.method == "POST":
        data = json.loads(request.body)
        event = Event.objects.create(
            title=data.get("title"),
            description=data.get("description", ""),
            start_time=data.get("start_time"),
            end_time=data.get("end_time"),
            user=request.user
        )
        return JsonResponse({"success": True, "event_id": event.id})
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

@login_required
@user_passes_test(is_admin)
def contact_view(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')      
        if name and email and subject and message:
            send_contact_form_email(name, email, subject, message)
            messages.success(request, "Your message has been sent successfully!")
            return redirect('contact')
        else:
            messages.error(request, "All fields are required. Please fill out the form completely.")  
    return render(request, "contact.html")

def contact(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        if first_name and last_name and email and subject and message:
            send_contact_form_email(first_name, last_name, email, subject, message)
            messages.success(request, "Your message has been sent successfully!")
            return redirect('contact')
        else:
            messages.error(request, "All fields are required. Please fill out the form completely.")

    return render(request, "contact.html")

@login_required
@user_passes_test(is_admin)
def dashboard(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        isbn = request.POST.get("isbn")
        cover_image = request.FILES.get("cover_image")
        genre_id = request.POST.get("genre")
        new_genre_name = request.POST.get("new_genre", "").strip()

        genre = None
        if new_genre_name:
            genre, _ = Genre.objects.get_or_create(name=new_genre_name)
        elif genre_id:
            genre = Genre.objects.get(id=genre_id)

        Book.objects.create(
            title=title,
            description=description,
            isbn=isbn,
            cover_image=cover_image,
            genre=genre,
        )
        messages.success(request, "Book added successfully!")
        return redirect("dashboard")

    context = {
        "total_books": Book.objects.count(),
        "total_reviews": Rating.objects.count(),
        "avg_rating": round(Rating.objects.aggregate(avg=Avg('rating'))['avg'] or 0, 2),
        "total_users": User.objects.count(),
        "latest_reviews": Rating.objects.select_related('creator', 'book').order_by('-created_at')[:5],
        "allow_replies": True,
        "books": Book.objects.all(),
        "users": User.objects.all(),
        "ratings": Rating.objects.select_related('creator', 'reply__responder'),
        "genres": Genre.objects.all(),
        "blocked_ips": BlockedIP.objects.all(),
    }
    return render(request, "dashboard.html", context)

@login_required
@user_passes_test(is_admin)
def get_events(request):
    """Fetch all events in JSON format."""
    events = Event.objects.all().values("title", "start_time", "end_time", "description")
    return JsonResponse(list(events), safe=False)

def calendar_view(request):
    """Render the calendar page."""
    return render(request, "calendar.html")

def add_genre_ajax(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        genre_name = data.get("name", "").strip()
        if genre_name:
            genre, created = Genre.objects.get_or_create(name=genre_name)
            return JsonResponse({"success": True, "genre_id": genre.id, "created": created})  
    return JsonResponse({"success": False})

def log_out(request):
    request.session.flush()
    return redirect('/')

def gallery(request):
    return render(request, "gallery.html", {"gallery_images": GalleryImage.objects.all()})

def all_reviews_for_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    all_reviews = book.ratings.all().order_by('-created_at')
    return render(request, 'all_reviews.html', {
        'book': book,
        'all_reviews': all_reviews
    })
def book(request, book_id):
    book = get_object_or_404(Book.objects.annotate(avg_rating=Avg('ratings__rating')), id=book_id)
    latest_reviews = book.ratings.all().order_by('-created_at')[:3]
    total_reviews = book.ratings.count()
    return render(request, 'book_review.html', {
        'book': book,
        'latest_reviews': latest_reviews,
        'total_reviews': total_reviews,
    })

@login_required
def add_review(request, book_id):
    """Allows users to leave ONE review & rating per book."""
    book = get_object_or_404(Book, id=book_id)
    
    existing_review = Rating.objects.filter(book=book, creator=request.user).first()
    if existing_review:
        messages.warning(request, "You've already reviewed this book. Want to update it?")
        return redirect('book', book_id=book.id)
    errors = Rating.objects.validator(request.POST)
    if errors:
        for message in errors.values():
            messages.error(request, message)
        return redirect('book', book_id=book.id)
    Rating.objects.create(
        book=book,
        rating=int(request.POST['rating']),
        review=request.POST['review'],
        creator=request.user
    )
@login_required
def edit_review(request, book_id):
    """Allows a user to edit their existing review for a book."""
    book = get_object_or_404(Book, id=book_id)
    review = Rating.objects.filter(book=book, creator=request.user).first()

    if not review:
        messages.error(request, "You haven't reviewed this book yet.")
        return redirect('book', book_id=book.id)

    if request.method == "POST":
        errors = Rating.objects.validator(request.POST)
        if errors:
            for message in errors.values():
                messages.error(request, message)
            return redirect('edit_review', book_id=book.id)

        if is_banned(request):
            messages.success(request, "Your review was updated!")  
            return redirect('books_home')

        review.rating = int(request.POST['rating'])
        review.review = request.POST['review']
        review.save()
        messages.success(request, "Your review has been updated.")
        return redirect('book', book_id=book.id)

    
    return render(request, 'edit_review.html', {
        'book': book,
        'review': review
    })

@login_required
def edit_review(request, book_id):
    """Allows a user to edit their existing review for a book."""
    book = get_object_or_404(Book, id=book_id)
    review = Rating.objects.filter(book=book, creator=request.user).first()
    if not review:
        messages.error(request, "You haven't reviewed this book yet.")
        return redirect('book', book_id=book.id)
    if request.method == "POST":
        errors = Rating.objects.validator(request.POST)
        if errors:
            for message in errors.values():
                messages.error(request, message)
            return redirect('edit_review', book_id=book.id)
        if is_banned(request):
         messages.success(request, "Your review was updated!")  # 😈
         return redirect('books_home')
        review.rating = int(request.POST['rating'])
        review.review = request.POST['review']
        review.save()
        messages.success(request, "Your review has been updated.")
        return redirect('book', book_id=book.id)
    return render(request, 'edit_review.html', {
        'book': book,
        'review': review
    })
    

@login_required
@user_passes_test(lambda u: u.is_staff)
def reply_to_review(request, review_id):
    review = get_object_or_404(Rating, id=review_id)
    if request.method == "POST":
        message = request.POST.get('message', '').strip()
        if not message:
            messages.error(request, "Reply message cannot be empty.")
            return redirect('book', book_id=review.book.id)
        # Prevent multiple replies
        if hasattr(review, 'reply'):
            messages.error(request, "You've already replied to this review.")
            return redirect('book', book_id=review.book.id)
        ReviewReply.objects.create(
            rating=review,
            responder=request.user,
            message=message
        )
        messages.success(request, "Reply posted successfully.")
        return redirect('book', book_id=review.book.id)
    return redirect('book', book_id=review.book.id)
# About Page
def about(request):
    return render(request, "about.html")
# Books Homepage (List of Books)
def books_home(request):
    books = Book.objects.annotate(avg_rating=Avg('ratings__rating'))  # ✅ Using 'ratings__rating' now
    for book in books:
        book.latest_reviews = book.ratings.all().order_by('-created_at')[:3]
    return render(request, 'books.html', {'books': books})

def calendar_view(request):
    """Display all upcoming events for users."""
    events = Event.objects.order_by('start_time')  # Sort by date
    return render(request, "calendar.html", {"events": events})

def new_review(request):
    return render(request,'add_review.html')
@login_required
@user_passes_test(is_admin)
def add_book(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        isbn = request.POST.get("isbn")
        cover_image = request.FILES.get("cover_image")
        genre_id = request.POST.get("genre")
        new_genre_name = request.POST.get("new_genre", "").strip()

        # Genre logic
        genre = None
        if new_genre_name:
            genre, _ = Genre.objects.get_or_create(name=new_genre_name)
        elif genre_id:
            genre = Genre.objects.filter(id=genre_id).first()

        # Book creation
        Book.objects.create(
            title=title,
            description=description,
            isbn=isbn,
            cover_image=cover_image,
            genre=genre
        )

        messages.success(request, "New book added successfully!")
        return redirect("dashboard")  # 👈 This is the key change

    return redirect("dashboard")  # Handles GET attempts gracefully to



