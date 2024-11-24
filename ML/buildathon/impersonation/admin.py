from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Celebrity, Impersonation

@admin.register(Celebrity)
class CelebrityAdmin(admin.ModelAdmin):
    list_display = ('name', 'tone')
    search_fields = ('name',)

@admin.register(Impersonation)
class ImpersonationAdmin(admin.ModelAdmin):
    list_display = ('celebrity', 'input_tweet', 'response', 'created_at')
    list_filter = ('celebrity', 'created_at')
    search_fields = ('input_tweet', 'response')
