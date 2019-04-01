from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    address = models.CharField(max_length=200)
    photo = models.ImageField()


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
    cover = models.ImageField()


class BookState(models.Model):
    state = models.CharField(max_length=30)


class BookGoals(models.Model):
    goal = models.CharField(max_length=30)


class BookInstance(models.Model):
    ISBN = models.ForeignKey(Book, on_delete=models.PROTECT)
    User = models.ForeignKey(User, on_delete=models.PROTECT)
    state = models.ForeignKey(BookState, on_delete=models.PROTECT)
    readingState = models.DecimalField(max_digits=4, decimal_places=3)
    goal = models.ForeignKey(BookGoals, on_delete=models.PROTECT)


class Proposal(models.Model):
    bookInstance = models.ForeignKey(BookInstance, on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, on_delete=models.PROTECT)


class TradeState(models.Model):
    state = models.CharField(max_length=20)


class Trade(models.Model):
    proposalID = models.OneToOneField(Proposal, on_delete=models.CASCADE)
    bookInstance2 = models.ForeignKey(BookInstance, on_delete=models.CASCADE)
    state = models.ForeignKey(TradeState, on_delete=models.PROTECT)
