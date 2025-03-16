from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login, logout
import morostav_site.models as models
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives

import bcrypt
User = get_user_model()  # ✅ Fetch custom user model dynamically

# Renders the login page
def dashboard(request):
    return render(request, 'dashboard.html')

# Creates a new user account
def user_create(request):
    user_manager = User.objects  # Explicitly reference the manager
    errors = user_manager.basic_validator(request.POST)  # Call it safely
    
    if errors:
        for k, v in errors.items():
            messages.error(request, v, extra_tags=k)
        return redirect('/register')

    # Extract user data
    first_name = request.POST['first_name']
    last_name = request.POST['last_name']
    email = request.POST['email']
    password = request.POST['password']
    # Create and save the new user
    user = user_manager.create_user(  # Ensuring we use the manager
        email=email,
        first_name=first_name,
        last_name=last_name,
        password=password
    )
    # Log the user in after registration
    login(request, user)
    messages.info(request, "Account created successfully!")
    return redirect('/books_home')

def to_login(request):
    return render(request,"login.html")


# Handles user login
def log_in(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Email not found.")
            return redirect('/login')
        # Verify the password
        if not user.check_password(password):
            messages.error(request, 'Incorrect password. Please try again.')
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
    text_content = strip_tags(html_content)  # Removes HTML tags for a plain-text fallback

    email = EmailMultiAlternatives(subject, text_content, 'noreply@morostavbooks.com', [user.email])
    email.attach_alternative(html_content, "text/html")
    email.send()
# Logs out the user and clears session
def log_out(request):
    logout(request)  # Logs user out
    messages.info(request, "You have been logged out.")
    # Optional: If needed, manually clear the session after logout.
    if request.session:
        request.session.flush()
    return redirect('/books_home')



def password_reset_complete(request):
    user = request.user  # Fetch the user (if applicable)
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