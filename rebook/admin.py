from rebook.models import *
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ['email', 'username', ]


# Register your models here.
admin.site.register(User)
admin.site.register(Author)
admin.site.register(Publisher)
admin.site.register(Book)
admin.site.register(BookState)
admin.site.register(BookGoals)
admin.site.register(BookInstance)
admin.site.register(Proposal)
admin.site.register(TradeState)
admin.site.register(Trade)

