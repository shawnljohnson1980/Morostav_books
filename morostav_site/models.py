from django.db import models
from django import forms
from django_starfield import Stars
from user_login_app.models import User



class BookManager(models.Manager):
    def validator(self,post_data):
        errors={}
        if len(post_data['title']) < 3 or len(post_data['title']) > 65:
            errors['title_length']="title must be between 3 and 65 Characters in length"
        if post_data['title']== post_data['title']:
            errors['title_unique']="Book already in the library"
        return errors

class RatingManager(models.Manager):
    def validator(self,post_data):
        errors={}
        if len(post_data['review'])< 10 or len(post_data['review'])> 400:
            errors['review_length']="Reviews must be at least 10 charcters long and less than 400 Cracters in length"
        return errors


class Rating(models.Model):
    rating = models.IntegerField()
    review=models.TextField()
    creator=models.ForeignKey(User,related_name='user_rating',on_delete=models.CASCADE)
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    objects=RatingManager()


class Book(models.Model):
    title=models.CharField(max_length=65)
    creator=models.ForeignKey(User,related_name='reviews',on_delete=models.CASCADE)
    rating=models.ManyToManyField(Rating,related_name='ratings', blank=True)
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    objects= BookManager()

