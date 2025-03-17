from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.decorators import login_required, user_passes_test
from django.apps import apps
User = get_user_model()

def is_admin(user):
    return user.is_authenticated and user.is_staff
@login_required()
@user_passes_test(is_admin)
def dashboard(request):
    return render(request, 'morostav_site/dashboard.html')

def admin_required(user):
    return bool(user and user.is_authenticated and user.is_staff)

def user_create(request):
    user_manager = User.objects  # Explicitly reference the manager
    errors = user_manager.basic_validator(request.POST)  # Call it safely
    if errors:
        for k, v in errors.items():
            messages.error(request, v, extra_tags=k)
            return redirect('/register')
    else:
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']  # Added username field
        email = request.POST['email']
        password = request.POST['password']

    user = user_manager.create_user(  
        username=username,  # Pass username into the model
        email=email,
        first_name=first_name,
        last_name=last_name,
        password=password
    )
    login(request, user)
    messages.info(request, f"Account for {username} created successfully!")
    return redirect('/books_home')


def to_login(request):
    return render(request,"login.html")


def log_in(request):
    if request.method == "POST":
        login_identifier = request.POST['login_identifier']  # Can be email or username
        password = request.POST['password']
        
        # Try to find the user by email or username
        user = None
        try:
            if "@" in login_identifier:
                user = User.objects.get(email=login_identifier)
            else:
                user = User.objects.get(username=login_identifier)
        except User.DoesNotExist:
            messages.error(request, "Username or Email not found.")
            return redirect('/login')

        # Check password
        if not user.check_password(password):
            messages.error(request, "Incorrect password. Please try again.")
            return redirect('/login')

        # Log the user in
        login(request, user)
        messages.info(request, "Login successful!")
        return redirect('/books_home')

    return render(request, "login.html")


def send_reset_email(user, domain, uid, token):
    subject = "Reset Your Password - Morostav Books"
    html_content = render_to_string('emails/reset_email.html',{
        'user': user,
        'domain': domain,
        'uid': uid,
        'token': token,
        'protocol': 'https',
    })
    text_content = strip_tags(html_content)  
    email = EmailMultiAlternatives(subject, text_content, 'noreply@morostavbooks.com', [user.email])
    email.attach_alternative(html_content, "text/html")
    email.send()

def log_out(request):
    logout(request)  
    messages.info(request, "You have been logged out.")
    if request.session:
        request.session.flush()
    return redirect('/books_home')

def password_reset_complete(request):
    user = request.user  
    send_mail(
        'Password Reset Successful',
        f'Hello {user.username},\n\nYour password has been reset successfully.',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
    return render(request, 'password_reset_complete.html')

def register(request):
    return render(request, "register.html")

def reset_start(request):
    return render(request, "reset_start.html")