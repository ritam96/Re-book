from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect 
from django.contrib.auth import authenticate, login as log, logout as outlog
from datetime import datetime
from rebook.models import User, Book, BookInstance, Trade, Proposal, TradeState
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

def dashboard(request):
    return render(request, 'proposalsGeneric.html')

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
    return render(request, 'trades.html', { 'trades': trades })

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


def bookDetails(request):
    book=Book.objects.get(ISBN=request.session['ISBN'])
    return render(request, 'bookDetails.html', {'book': book})

def logout(request):
    outlog(request)
    return redirect('rebook')
