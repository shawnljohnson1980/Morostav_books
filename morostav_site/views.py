from django.shortcuts import render,HttpResponse,redirect
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Book, Rating
from django.db.models import Count  
from django.contrib.auth.decorators import user_passes_test

def admin_required(user):
    return user.is_authenticated and user.is_staff  

def home(request):
    return render(request,"books_home.html")


def send_contact_form_email(name, email, subject, message):
    subject_line = f"New Contact Form Submission: {subject}"
    html_message = render_to_string('emails/contact_form_submission.html', {
        'name': name,
        'email': email,
        'subject': subject,
        'message': message,
        'protocol': 'https' if settings.USE_HTTPS else 'http',
        'domain': settings.ALLOWED_HOSTS[0],  # Ensure ALLOWED_HOSTS is set correctly
    })
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [settings.CONTACT_EMAIL]  # Add your support email here
    
    send_mail(subject_line, plain_message, from_email, to_email, html_message=html_message)

def contact_view(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        if name and email and subject and message:
            send_contact_form_email(name, email, subject, message)
            messages.success(request, "Your message has been sent successfully!")
            return redirect('/contact')
        else:
            messages.error(request, "All fields are required. Please fill out the form completely.")

    return render(request, "contact.html")

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Book, Rating, User

@login_required
@admin_required
def dashboard(request):
    # Count total books
    total_books = Book.objects.count()
    
    # Count total reviews
    total_reviews = Rating.objects.count()
    
    # Average rating (if applicable)
    avg_rating = Rating.objects.aggregate(avg=models.Avg('rating'))['avg'] or 0
    
    # Total users
    total_users = User.objects.count()

    # Latest reviews (limit 5)
    latest_reviews = Rating.objects.select_related('creator', 'book').order_by('-created_at')[:5]

    context = {
        "total_books": total_books,
        "total_reviews": total_reviews,
        "avg_rating": round(avg_rating, 2),
        "total_users": total_users,
        "latest_reviews": latest_reviews,
    }
    return render(request, "dashboard.html", context)


def index(request):
    print(request.session['user_id'])
    user=User.objects.get(id=request.session['user_id'])
    # printing user id   
    print('*****************************')
    print(user.id)
    rating=Rating.objects.all()
    context={
    'user':user,
    'ratings':rating
    }
    return render(request,'book_home.html',context)


def log_out(request):
   request.session.flush()
   return redirect('/')

def process(request):
    errors = Book.objects.validator(request.POST)
    Rating.objects.validator(request.POST)
    Book.objects.validator(request.POST)
    if errors:
        for k, v in errors.items():
            messages.error(request, v,extra_tags=k)
            return redirect('/books/new')
    try:
        rating = request.POST['rating'],
        review= request.POST['review'],
        creator= request.session['user_id']
    except:
        rating = ''
        review =''
        creator =''
    try:
        rating = request.POST['rating']
        review = request.POST['review']
        creator=request.POST['user_id']
    except:
        rating = ''
        review =''
        creator=''
    # Rating Check / Create
    if rating.isnumeric():
       rating_obj = Rating.objects.get(id=rating)
       print(rating_obj.rating,rating_obj.review,rating_obj.creator)
    try:
        book=request.POST['book'],
        user=User.objects['user_id'],
        title = request.POST['title'],
        creator= user,
        rating=request.POST['rating']
    except:
        title = ''
        creator =''
        rating=''
    try:
        title= request.POST['title'],
        creator=user,
        rating=rating
    except:
       title = ''
       author =''
       creator=''
       rating=''
    # Rating Check / Create
    if Book.isnumeric():
       book_obj = Book.objects.get(id=book)
       print(book_obj.title,book_obj.book_obj.creator,book_obj.rating)
    else:
        new_book=Book(title=title,rating=rating,creator=user)
        new_book.save()
        print(new_book)
        print(new_book)
        new_rating = Rating(rating=rating,review=review,creator=creator)
        new_rating.save()
        print(new_rating)
    # Book Check / Create
    return redirect('/new')