from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login, logout
from morostav_site.models import Book,Rating,ReviewReply
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.decorators import login_required, user_passes_test
from django.apps import apps
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import BlockedIP


 # Optional: Where users go after logout
User = get_user_model()
def is_admin(user):
    return user.is_authenticated and user.is_staff

@login_required()
@user_passes_test(is_admin)
def dashboard(request):
    return render(request, "dashboard.html")

def admin_required(user):
    return bool(user and user.is_authenticated and user.is_staff)

def user_create(request):
    user_manager = User.objects  # Explicitly reference the manager
    errors = user_manager.basic_validator(request.POST)  # Call it safely
    if errors:
        for k, v in errors.items():
            messages.error(request, v, extra_tags=k)
            return redirect('register')
    else:
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']  # Added username field
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
    user = user_manager.create_user(  
        username=username,  # Pass username into the model
        email=email,
        first_name=first_name,
        last_name=last_name,
        password=password,
        confrim_password=confirm_password
    )
    log_in(request, user)
    messages.info(request, f"Account for {username} created successfully!")
    return redirect('home')

def to_login(request):
    return render(request,"login.html")


def log_in(request):
    if request.method == "POST":
        login_identifier = request.POST.get("login_identifier", "").strip()  # Can be email or username
        password = request.POST.get("password", "").strip()
        # Ensure fields are not empty
        if not login_identifier or not password:
            messages.error(request, "Please fill in both fields.")
            return redirect("to_login")
        # Try to authenticate using username/email + password
        user = None
        if "@" in login_identifier:  # Checking if it's an email
            user = User.objects.filter(email=login_identifier).first()
        else:
            user = User.objects.filter(username=login_identifier).first()
        if user:
            authenticated_user = authenticate(request, username=user.username, password=password)
            if authenticated_user:
                login(request, authenticated_user)
                messages.success(request, "Login successful!")
                return redirect("home")  # Redirect to homepage after login
            else:
                messages.error(request, "Incorrect password. Please try again.")
        else:
            messages.error(request, "Username or Email not found.")
        return redirect("to_login")  # Redirect back to login page on failure


def send_reset_email(user, domain, uid, token):
    subject = "Reset Your Password - Morostav Books"
    html_content = render_to_string('registration/password_reset_success.html',{
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

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # Needed because sendBeacon skips CSRF
def log_out(request):
    if request.user.is_authenticated:
        logout(request)
        request.session.flush()
        return JsonResponse({"message": "Logged out on unload"})
    return JsonResponse({"message": "No active session"}, status=204)


def password_reset_done(request):
    user = request.user  
    send_mail(
        'Password Reset Successful',
        f'Hello {user.username},\n\nYour password has been reset successfully.',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
    return render(request, 'registration/password_reset_complete.html')

def register(request):
    return render(request, "register.html")

def reset_start(request):
    return render(request, "reset_start.html")

@user_passes_test(lambda u: u.is_staff)
def ban_ip(request):
    if request.method == 'POST':
        ip = request.POST.get('ip')
        if ip:
            BlockedIP.objects.get_or_create(ip_address=ip)
            return JsonResponse({'success': True, 'message': f'{ip} has been blocked.'})
    return JsonResponse({'success': False, 'message': 'Invalid IP.'}, status=400)

def banned_ip_list(request):
    if not request.user.is_staff:
        return JsonResponse({"error": "Forbidden"}, status=403)
    
    blocked_ips = BlockedIP.objects.all()
    return render(request, "morostav_site/banned_ips.html", {"blocked_ips": blocked_ips})

@csrf_exempt
def unban_ip(request):
    if request.method == "POST" and request.user.is_staff:
        data = json.loads(request.body)
        ip = data.get("ip_address")
        try:
            BlockedIP.objects.filter(ip_address=ip).delete()
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request"})




