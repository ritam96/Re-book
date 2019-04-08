from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect 
from django.contrib.auth import authenticate, login as log, logout as outlog
from datetime import datetime
from rebook.models import User, Book, BookInstance, Trade, Proposal, TradeState, BookGoals
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
    pass


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
