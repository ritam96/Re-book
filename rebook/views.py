from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect 
from django.contrib.auth import authenticate, login as log, logout as outlog
from datetime import datetime
from rebook.models import User, Book, BookInstance
from django.core import serializers
from django.db import connection
from django.template.defaulttags import register

# Create your views here.
def rebook(request):
    if not request.user.is_anonymous:
        user = User.objects.get(id = request.user.id)
        request.session["hasNotifications"] = user.hasNotifications
    else:
        request.session["hasNotifications"] = False

    return render(request, 'layout.html')

def browse(request):
    queryset = Book.objects.order_by("-year")[:10]

    bookRatingsDict = {}
    for book in queryset:
        cursor = connection.cursor()
        cursor.execute("SELECT AVG(rating_id) as Average FROM (SELECT * FROM rebook_bookinstance WHERE ISBN_id=" + book.ISBN + ")")
        result = cursor.fetchall()
        if result[0][0] != None:
            bookRatingsDict[book] = result[0][0]
            
        else:
            bookRatingsDict[book] = "No reviews yet!"

    return render(request, 'browse.html', {'queryset': queryset, 'bookRatingsDict': bookRatingsDict})
    


def login(request):
    return render(request, 'login.html', {'registering': False})

def register(request):
    return render(request, 'login.html', {'registering': True})

def loginWithCredentials(request):
    user = authenticate(username=request.POST['username'], password=request.POST['password'])
    if user is not None:
        log(request, user)
        # Redirect to a success page.
        return redirect('rebook')
    else:
        return HttpResponse("Your username and password didn't match.")

def createAccount(request):
    user = User.objects.create_user(username=request.POST['username'],
                                    email=request.POST['email'],
                                    password=request.POST['password'],
                                    address=request.POST['address'],
                                    photo = request.POST['photo'])
    if 'photo' in request.POST.keys():
        user.photo = request.POST['photo']

    log(request, user)

    return redirect('rebook')        

def logout(request):
    outlog(request)
    return redirect('rebook')
