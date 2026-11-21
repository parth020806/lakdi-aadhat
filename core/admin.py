from django.contrib import admin
from .models import Enquiry, WoodRate


@admin.register(WoodRate)
class WoodRateAdmin(admin.ModelAdmin):
    list_display = ("wood_type", "rate_per_quintal", "updated_on", "is_visible")
    list_editable = ("rate_per_quintal", "is_visible")


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "company", "created_at", "handled")
    list_filter = ("handled",)
    search_fields = ("name", "phone", "company")
