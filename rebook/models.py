from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.files.storage import FileSystemStorage

# Create your models here.
fs = FileSystemStorage(location='/media/covers')

class User(AbstractUser):
    address = models.CharField(max_length=200)
    photo = models.ImageField()
    hasNotifications = models.BooleanField(default=False)


class Author(models.Model):
    name = models.CharField(max_length=70)


class Publisher(models.Model):
    name = models.CharField(max_length=70)


class Book(models.Model):
    ISBN = models.CharField(max_length=20, primary_key=True)
    title = models.CharField(max_length=100)
    author = models.ManyToManyField(Author)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    year = models.IntegerField()
    cover = models.ImageField(storage=fs)


class BookState(models.Model):
    state = models.CharField(max_length=30)


class BookGoals(models.Model):
    goal = models.CharField(max_length=30)

class Ratings(models.Model):
    numberStars = models.IntegerField(primary_key=True)
    rating = models.CharField(max_length=20)

class BookInstance(models.Model):
    ISBN = models.ForeignKey(Book, on_delete=models.PROTECT)
    User = models.ForeignKey(User, on_delete=models.PROTECT)
    state = models.ForeignKey(BookState, on_delete=models.PROTECT)
    readingState = models.DecimalField(max_digits=4, decimal_places=3)
    goal = models.ForeignKey(BookGoals, on_delete=models.PROTECT)
    rating = models.ForeignKey(Ratings, on_delete=models.PROTECT, default=None, null=True)

class TradeState(models.Model):
    state = models.CharField(max_length=20)

class Proposal(models.Model):
    bookInstance = models.ForeignKey(BookInstance, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    user2 = models.ForeignKey(User, on_delete=models.PROTECT)
    state = models.ForeignKey(TradeState, on_delete=models.PROTECT)



class Trade(models.Model):
    proposalID = models.OneToOneField(Proposal, on_delete=models.CASCADE)
    bookInstance2 = models.ForeignKey(BookInstance, on_delete=models.CASCADE)
    state = models.ForeignKey(TradeState, on_delete=models.PROTECT)
