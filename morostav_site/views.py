from django.shortcuts import render,HttpResponse

# Create your views here.
def home(request):
    return render(request,"books_home.html")


