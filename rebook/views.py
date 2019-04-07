from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect 
from django.contrib.auth import authenticate, login as log, logout as outlog
from datetime import datetime
from rebook.models import User, Book, BookInstance, Trade
from django.core import serializers
from django.db import connection
from django.template.defaulttags import register
import itertools

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


def bookDetails(request):
    book=Book.objects.get(ISBN=request.session['ISBN'])
    return render(request, 'bookDetails.html', {'book': book})


def editProfile(request):
    return render(request, 'editProfile.html')


def account(request):
    return render(request, 'account.html')


def edit(request):
    user = User.objects.get(username=request.user)
    print(user)
    if 'email' in request.POST.keys() and request.POST['email'] != '':
        print(request.POST['email'])
        user.email = request.POST['email']
    if 'address' in request.POST.keys() and request.POST['address'] != '':
        user.address = request.POST['address']
    if 'password' in request.POST.keys() and request.POST['password'] != '':
        user.set_password(request.POST['password'])
        log(request, user)
    if 'photo' in request.POST.keys() and request.POST['photo'] in request.FILES:
        user.photo = request.POST['photo']
    user.save()
    return redirect('account')


def logout(request):
    outlog(request)
    return redirect('rebook')


def search(request):
    print(request.POST['query'])
    query = request.POST['query']
    books_tittle = Book.objects.filter(title__contains=query)
    books_author = Book.objects.filter(author__name__contains=query)
    books_publisher = Book.objects.filter(publisher__name__contains=query)
    books = list(itertools.chain(books_tittle, books_author, books_publisher))
    bookRatingsDict = {}
    for book in books:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT AVG(rating_id) as Average FROM (SELECT * FROM rebook_bookinstance WHERE ISBN_id=" + book.ISBN + ")")
        result = cursor.fetchall()
        if result[0][0] != None:
            bookRatingsDict[book] = result[0][0]

        else:
            bookRatingsDict[book] = "No reviews yet!"

    print(books)

    return render(request, 'filteredBooks.html', {'books': books, 'bookRatingsDict': bookRatingsDict})

def deleteUser(request):
    User.objects.filter(username=request.user).delete()
    return redirect('rebook')
