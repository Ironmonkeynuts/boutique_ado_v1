from django.shortcuts import render

# Create your views here.


def index(request):
    '''
    This is the home page for the application.
    It will display a welcome message and a link to the login page.
    '''
    return render(request, 'home/index.html')
