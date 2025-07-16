from django.shortcuts import render

# Create your views here.
"""
If we don't use singnals
# users/views.py
from django.http import HttpResponse
from django.contrib.auth.models import User
from .models import Profile, UserLog

def create_user(request):
    # Hardcoded profile creation and logging in view
    username = request.POST.get('username', 'testuser')
    email = request.POST.get('email', 'test@example.com')
    user = User.objects.create(username=username, email=email)
    # Tightly coupled profile creation
    Profile.objects.create(user=user, bio=f"Bio for {username}")
    # Tightly coupled logging
    UserLog.objects.create(user=user, action=f"User {username} created")
    return HttpResponse(f"User {username} created with profile!")

def update_user_email(request, user_id):
    user = User.objects.get(id=user_id)
    new_email = request.POST.get('email', 'new@example.com')
    # Hardcoded logging in view
    if user.email != new_email:
        user.email = new_email
        user.save()
        UserLog.objects.create(user=user, action=f"Email updated to {new_email}")
    return HttpResponse(f"User {user.username}'s email updated!")
"""

from django.http import HttpResponse
from django.contrib.auth.models import User

def create_user(request):
    username = request.POST.get('username', 'testuser')
    email = request.POST.get('email', 'test@example.com')
    user = User.objects.create(username=username, email=email)
    return HttpResponse(f"User {username} created!")

def update_user_email(request, user_id):
    user = User.objects.get(id=user_id)
    new_email = request.POST.get('email', 'new@example.com')
    user.email = new_email
    user.save()
    return HttpResponse(f"User {user.username}'s email updated!")