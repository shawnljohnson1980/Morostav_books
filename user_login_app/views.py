from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from morostav_site.models import Book, Rating, ReviewReply
from .models import BlockedIP
import json

User = get_user_model()

def send_verification_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, OverflowError, TypeError):
        user = None

    if user and default_token_generator.check_token(user, token):
        # Already valid; maybe inform user it's been verified already
        return redirect("home")

    if user:
        new_token = default_token_generator.make_token(user)
        new_uid = urlsafe_base64_encode(force_bytes(user.pk))
        link = f"{request.scheme}://{request.get_host()}/verify_email/{new_uid}/{new_token}/"

        subject = "Verify your email for Morostav Books"
        message = render_to_string("email/verify_email.html", {
            "user": user,
            "verification_link": link,
            "domain": request.get_host(),
            "protocol": request.scheme,
        })

        send_mail(subject, "", settings.DEFAULT_FROM_EMAIL, [user.email], html_message=message)

    return redirect("verified") 

def is_admin(user):
    return user.is_authenticated and user.is_staff

@login_required()
@user_passes_test(is_admin)
def dashboard(request):
    return render(request, "dashboard.html")

def admin_required(user):
    return bool(user and user.is_authenticated and user.is_staff)

def user_create(request):
    if request.method == "POST":
        user_manager = User.objects

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        try:
            user = user_manager.create_user(
                email=email,
                username=username,
                first_name=first_name,
                last_name=last_name,
                password=password,
                confirm_password=confirm_password,
            )

            authenticated_user = authenticate(request, username=username, password=password)

            if authenticated_user:
                login(request, authenticated_user)
                messages.info(request, f"Account for {username} created successfully!")
                return redirect('home')
            else:
                messages.error(request, "Authentication failed after registration. Please log in manually.")
                return redirect("to_login")

        except ValueError as ve:
            messages.error(request, str(ve))
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            return redirect("send_verification_email", uidb64=uid, token=token)
        
def send_verification_email(request, uidb64, new_token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, OverflowError, TypeError):
        user = None

    if user:
        new_token = default_token_generator.make_token(user)
        new_uid = urlsafe_base64_encode(force_bytes(user.pk))
        link = f"{request.scheme}://{request.get_host()}/verify_email/{new_uid}/{new_token}/"

        subject = "Verify your email for Morostav Books"
        message = render_to_string("email/verify_email.html", {
            "user": user,
            "verification_link": link,
            "domain": request.get_host(),
            "protocol": request.scheme,
        })
        send_mail(subject, "", settings.DEFAULT_FROM_EMAIL, [user.email], html_message=message)

    messages.info(request, "Verification email sent.")
    return redirect("home")

def verified(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError, OverflowError):
        user = None
    if user and default_token_generator.check_token(user, token):
        user.is_active = True  
        user.save()
        messages.success(request, "Email verified successfully!")
        return render(request, "verify.html")
    else:
        messages.error(request, "Invalid or expired verification link.")
        return redirect("home")

def log_in(request):
    if request.method == "POST":
        login_identifier = request.POST.get("login_identifier", "").strip() 
        password = request.POST.get("password", "").strip()
        if not login_identifier or not password:
            messages.error(request, "Please fill in both fields.")
            return redirect("to_login")
        user = None
        if "@" in login_identifier:  
            user = User.objects.filter(email=login_identifier).first()
        else:
            user = User.objects.filter(username=login_identifier).first()
        if user:
            authenticated_user = authenticate(request, username=user.username, password=password)
            if authenticated_user:
                login(request, authenticated_user)
                messages.success(request, "Login successful!")
                return redirect("home")  
            else:
                messages.error(request, "Incorrect password. Please try again.")
        else:
            messages.error(request, "Username or Email not found.")
        return redirect("to_login") 

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

@csrf_exempt 
def log_out(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect("home")

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

