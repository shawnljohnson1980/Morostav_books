from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
import morostav_site.models as models
import bcrypt

# Renders the login page
def dashboard(request):
    return render(request, 'dashbaord.html')

# Creates a new user account
def user_create(request):
    errors = User.objects.basic_validator(request.POST)
    
    if errors:
        for k, v in errors.items():
            messages.error(request, v, extra_tags=k)
        return redirect('/')

    # Check if the email is already registered
    if User.objects.filter(email=request.POST['email']).exists():
        messages.error(request, "Email already in use. Try logging in.")
        return redirect('/')

    # Extract user data
    first_name = request.POST['first_name']
    last_name = request.POST['last_name']
    email = request.POST['email']
    password = request.POST['password']

    # Hash the password
    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    print(f"DEBUG: Password hash - {pw_hash}")

    # Create and save the new user
    user = User.objects.create(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=pw_hash,
    )

    # Store user_id in session after successful registration
    request.session['user_id'] = user.id
    messages.info(request, "Account created successfully!")
    
    return redirect('/books_home')

# Handles user login
def login(request,user_id):
    try:
        user = User.objects.get(email=request.POST['email'])
    except User==(request.POST['User_id']):
        messages.error(request, "Email not found.")
        return redirect('/')

    # Verify the password
    if not bcrypt.checkpw(request.POST['password'].encode(), user.password.encode()):
        messages.error(request, 'Incorrect password. Please try again.')
        return redirect('/login.html')

    # Store user_id in session after successful login
    request.session['user_id'] = user.id
    messages.info(request, "Login successful!")
    
    return redirect('/books_home')

# Logs out the user and clears session
def log_out(request):
    if 'user_id' in request.session:
        del request.session['user_id']
        request.session.flush()
    messages.info(request, "You have been logged out.")
    return redirect('/books_home')

def log_in(request):
    return render(request,"login.html")

def register(request):
    return render(request,"register.html")

def reset_start(request):
    return render(request, "reset_start.html")