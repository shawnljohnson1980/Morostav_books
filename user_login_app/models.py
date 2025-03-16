import re
from django.db import models

class UserManager(models.Manager):
    def basic_validator(self, post_data):
        errors = {}
        email_regex = re.compile(
            r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$'
        )
        # Validate email format
        if not email_regex.match(post_data['email']):
            errors['email_pattern'] = "Invalid email address format. Please provide name@domain.com"
        # Ensure email is unique
        if User.objects.filter(email=post_data['email']).exists():
            errors['email_unique'] = "Email is already in use. Please try logging in."
        # Password length 
        if len(post_data['password']) < 8 or len(post_data['password']) > 60:
            errors['password_length'] = "Password must be between 8 and 60 characters long."
        # Password confirmation check
        if post_data['password'] != post_data['confirm_password']:
            errors['password_match'] = "Passwords do not match."
        # First name validation
        if len(post_data['first_name']) < 5 or len(post_data['first_name']) > 45:
            errors['first_name_length'] = "First name must be between 5 and 45 characters long."
        # Last name validation
        if len(post_data['last_name']) < 5 or len(post_data['last_name']) > 45:
            errors['last_name_length'] = "Last name must be between 5 and 45 characters long."
        return errors


def create_superuser(self, email, first_name, last_name, password):
        user = self.create_user(email, first_name, last_name, password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
    
class User(models.Model):
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    email = models.CharField(max_length=200)
    password = models.CharField(max_length=60)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = UserManager()