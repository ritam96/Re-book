from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from datetime import datetime


# Create your views here.
def rebook(request):
    return render(request, 'layout.html')


def login(request):
    return render(request, 'login.html')
