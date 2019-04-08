"""re_book URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rebook import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('logout/', views.logout),
    path('', views.browse, name='rebook'),
    path('login/', views.login),
    path('loginWithCredentials', views.loginWithCredentials),
    path('register', views.register),
    path('createAccount', views.createAccount),
    path('browse/', views.browse),
    path('proposals', views.proposals, name='proposals'),
    path('offers', views.offers, name='offers'),
    path('trades', views.trades, name='trades'),
    path('rejectoffer', views.rejectProposal, name="rejectoffer"),
    path('acceptoffer/', views.acceptProposal, name="acceptoffer"),
    path('acceptTrade', views.acceptTrade, name="acceptTrade"),
    path('confirmTrade/', views.confirmTrade, name="confirmTrade"),
    path('rejectTrade/', views.rejectTrade, name="rejectTrade"),
    path('bookDetails', views.bookDetails),
    path('addBookToCollection', views.addBookToCollection),
    path('account/', views.account, name='account'),
    path('editProfile/', views.editProfile, name='editProfile'),
    path('edit/', views.edit),
    path('search/', views.search),
    path('deleteUser/', views.deleteUser),
    path('booksForSale/<str:isbn>', views.booksForSale, name='booksForSale'),
    path('booksForTrade/<str:isbn>', views.booksForTrade, name='booksForTrade')
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

