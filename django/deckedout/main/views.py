from django.shortcuts import render

# Create your views here.

def home(request):

    return render(request, 'main/index.html')


def about(request):
    
    return render(request, 'main/about.html')


def skateboards(request):
    
    return render(request, 'main/skateboards.html')

def login(request):
    
    return render(request, 'main/login.html')

def signup(request):
    
    return render(request, 'main/signup.html')
