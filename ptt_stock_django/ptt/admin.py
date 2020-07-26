from django.contrib import admin

# Register your models here.
from ptt.models import Ptt, Stock

admin.site.register(Ptt)
admin.site.register(Stock)