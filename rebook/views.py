from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect 
from django.contrib.auth import authenticate, login as log, logout as outlog
from datetime import datetime
from rebook.models import *
from django.core import serializers
from django.db import connection
from django.template.defaulttags import register
import itertools
import math

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
            rating = float(result[0][0])
            integer = rating.is_integer()
            final = ['star']
            fullStar = math.floor(rating)
            if integer is False:
                final.append('star-half')
            i = 1
            star = ['star']
            while i < fullStar:
                final = star + final
                i += 1

            bookRatingsDict[book] = final
            
        else:
            bookRatingsDict[book] = []

    return render(request, 'browse.html', {'queryset': queryset, 'bookRatingsDict': bookRatingsDict})


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

def proposals(request):
    user = User.objects.get(username=request.user)
    my_proposals = Proposal.objects.filter(user2=user.id)
    return render(request, 'proposals.html', { 'my_proposals': my_proposals })

def offers(request):
    user = User.objects.get(username=request.user)
    offers = Proposal.objects.raw('''SELECT * FROM rebook_proposal 
        JOIN rebook_bookinstance ON bookinstance_id=rebook_bookinstance.id 
        WHERE rebook_proposal.state_id=3 AND User_id=''' + str(user.id))
    return render(request, 'offers.html', { 'offers': offers })

def trades(request):
    user = User.objects.get(username=request.user)
    trades = Trade.objects.raw('''SELECT * FROM rebook_trade
        JOIN rebook_bookinstance ON bookinstance2_id=rebook_bookinstance.id
        WHERE rebook_trade.state_id=3 AND rebook_bookinstance.User_id=''' + str(user.id))

    finished = Trade.objects.raw('''SELECT * FROM rebook_trade
        JOIN rebook_bookinstance ON bookinstance2_id=rebook_bookinstance.id
        JOIN rebook_proposal ON proposalID_id=rebook_proposal.id
        WHERE rebook_trade.state_id!=3 AND rebook_bookinstance.User_id=''' + str(user.id))
    
    remaining = Trade.objects.raw('''SELECT * FROM rebook_trade
        JOIN rebook_proposal ON proposalID_id=rebook_proposal.id
        JOIN rebook_bookinstance ON rebook_proposal.bookinstance_id=rebook_bookinstance.id
        WHERE rebook_trade.state_id!=3 AND rebook_bookinstance.User_id=''' + str(user.id))
    
    return render(request, 'trades.html', { 'trades': trades, 'finished': finished, 'remaining': remaining })

def rejectProposal(request):
    proposal = request.POST["offer"]
    state = TradeState.objects.get(id=2)
    Proposal.objects.filter(id=proposal).update(state=state)
    return redirect('offers')

def acceptProposal(request):
    proposal = Proposal.objects.get(id=request.POST["offer"])
    user = User.objects.get(id=request.POST["user"])
    books = BookInstance.objects.filter(User=user)
    return render(request, 'makeTrade.html', { 'proposal': proposal, 'books': books, 'user': user })


def acceptTrade(request):
    proposal = Proposal.objects.get(id=request.POST["proposal"])
    book = BookInstance.objects.get(id=request.POST["book"])
    pending = TradeState.objects.get(id=3)
    trade = Trade(proposalID=proposal, bookInstance2=book, state=pending)
    trade.save()

    trading = TradeState.objects.get(id=4)
    Proposal.objects.filter(id=request.POST["proposal"]).update(state=trading)
    return redirect('offers')

def confirmTrade(request):
    trade = Trade.objects.get(id=request.POST['trade'])
    proposal = trade.proposalID
    accepted = TradeState.objects.get(id=1)
    Trade.objects.filter(id=request.POST['trade']).update(state=accepted)
    Proposal.objects.filter(id=proposal.id).update(state=accepted)
    return redirect('trades')

def rejectTrade(request):
    trade = Trade.objects.get(id=request.POST['trade'])
    proposal = trade.proposalID
    accepted = TradeState.objects.get(id=2)
    Trade.objects.filter(id=request.POST['trade']).update(state=accepted)
    Proposal.objects.filter(id=proposal.id).update(state=accepted)
    return redirect('trades')

def bookDetails(request):
    book=Book.objects.get(ISBN=request.GET['bookISBN'])
    rating = None

    # Calculate average rating
    cursor = connection.cursor()
    cursor.execute("SELECT AVG(rating_id) as Average FROM (SELECT * FROM rebook_bookinstance WHERE ISBN_id=" + book.ISBN + ")")
    result = cursor.fetchall()
    if result[0][0] != None:
        rating = result[0][0] 
    else:
        rating = "No reviews yet!"

    return render(request, 'bookDetails.html', {'book': book, 'rating': rating})


def booksForSale(request, isbn):
    book = Book.objects.get(ISBN=isbn)
    instancesForSale = BookInstance.objects.raw('''SELECT * FROM rebook_bookinstance
    WHERE goal_id=1 AND ISBN_id='''+str(isbn))
    rating = None

    # Calculate average rating
    cursor = connection.cursor()
    cursor.execute(
        "SELECT AVG(rating_id) as Average FROM (SELECT * FROM rebook_bookinstance WHERE ISBN_id=" + book.ISBN + ")")
    result = cursor.fetchall()
    if result[0][0] != None:
        rating = result[0][0]
    else:
        rating = "No reviews yet!"
    return render(request, 'booksForSale.html', {'book': book, 'instances': instancesForSale, 'rating': rating})


def booksForTrade(request, isbn):
    book = Book.objects.get(ISBN=isbn)
    instancesForTrade = BookInstance.objects.raw('''SELECT * FROM rebook_bookinstance
    WHERE goal_id=4 AND ISBN_id='''+str(isbn))
    rating = None

    # Calculate average rating
    cursor = connection.cursor()
    cursor.execute(
        "SELECT AVG(rating_id) as Average FROM (SELECT * FROM rebook_bookinstance WHERE ISBN_id=" + book.ISBN + ")")
    result = cursor.fetchall()
    if result[0][0] != None:
        rating = result[0][0]
    else:
        rating = "No reviews yet!"
    return render(request, 'booksForSale.html', {'book': book, 'instances': instancesForTrade, 'rating': rating})


def addBookToCollection(request):

    book = Book.objects.get(ISBN=request.POST['ISBN'])
    bookInstance = BookInstance(User=request.user, ISBN=book)
    if 'readingState' in request.POST.keys() and request.POST['readingState'] != '':
        bookInstance.readingState = request.POST['readingState']
    if 'bookGoals' in request.POST.keys() and request.POST['bookGoals'] != '':
        bookGoals = BookGoals.objects.get(id=int(request.POST['bookGoals']))
        bookInstance.goal = bookGoals
    if 'bookState' in request.POST.keys() and request.POST['bookState'] != '':
        bookState = BookState.objects.get(id=int(request.POST['bookState']))
        bookInstance.state = bookState
    if 'bookRating' in request.POST.keys() and request.POST['bookRating'] != '':
        bookRating = Ratings.objects.get(numberStars=int(request.POST['bookRating']))
        bookInstance.rating = bookRating

    if 'price' in request.POST.keys() and request.POST['price'] != '':
        bookInstance.price = float(request.POST['price'])

    bookInstance.save()

    return redirect('collection')


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
        myfile = request.FILES['photo']
        fs = FileSystemStorage('media/photos')
        filename = fs.save(myfile.name, user.username)
        user.photo = fs.url(filename)
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
            rating = float(result[0][0])
            integer = rating.is_integer()
            final = ['star']
            fullStar = math.floor(rating)
            if integer is False:
                final.append('star-half')
            i = 1
            star = ['star']
            while i < fullStar:
                final = star + final
                i += 1

            bookRatingsDict[book] = final

        else:
            bookRatingsDict[book] = []

    print(books)

    return render(request, 'filteredBooks.html', {'books': books, 'bookRatingsDict': bookRatingsDict})

def deleteUser(request):
    User.objects.filter(username=request.user).delete()
    return redirect('rebook')

def collection(request):
    user = User.objects.get(username=request.user.username)
    cursor = connection.cursor()
    cursor.execute("SELECT ISBN, title, cover, readingState , rating_id FROM rebook_bookinstance JOIN rebook_book ON rebook_bookinstance.ISBN_id = rebook_book.ISBN WHERE User_id="+ str(user.id))
    result = cursor.fetchall()
    books = [];
    for book in result:
        tempBook = {}
        tempBook["ISBN"] = book[0]
        tempBook["title"] = book[1]
        tempBook["cover"] = "/media/" + book[2]
        tempBook["readingState"] = str(book[3]*100) + "%"

        if book[4] == None:
            tempBook["rating"] = []

        else:
            rating = float(book[4])
            integer = rating.is_integer()
            final = ['star']
            fullStar = math.floor(rating)
            if integer is False:
                final.append('star-half')
            i=1
            star=['star']
            while i < fullStar:
                final = star + final
                i+=1

            tempBook["rating"] = final
        books.append(tempBook)

    print(books)

    return render(request, 'collection.html', {'books': books})


def searchCollection(request):
    #print(request.POST['query'])

    #return render(request, 'collection.html')

    pass

def sell(request, isbn, username):
    print(isbn)
    user = User.objects.get(username=username)
    b = Book.objects.get(ISBN=isbn)
    book = BookInstance.objects.get(ISBN=b, User=user.id)

    purchase = Purchases(bookInstance = book, buyer = request.user)
    purchase.save()
    return redirect('collection')

def listPurchases(request):
    user = User.objects.get(username=request.user)
    my_purchases = Purchases.objects.filter(buyer=user.id)
    return render(request, 'purchases.html', { 'my_purchases': my_purchases })

def sold(request):
    b = BookInstance.objects.filter(User=request.user)
    my_purchases = []
    for book in b:
        if len(Purchases.objects.filter(bookInstance=book)) != 0:
            my_purchases.append(Purchases.objects.get(bookInstance=book))
    return render(request, 'sold.html', {'my_purchases': my_purchases})
    