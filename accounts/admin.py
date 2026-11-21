from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "company", "phone", "is_approved")
    list_filter = ("role", "is_approved")
    list_editable = ("role", "is_approved")
    search_fields = ("user__username", "company", "phone")
