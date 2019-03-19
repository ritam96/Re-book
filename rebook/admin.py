from django.contrib import admin
from rebook.models import *

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

