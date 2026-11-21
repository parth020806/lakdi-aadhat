from django.contrib import admin
from .models import Consignment, Party, Payment, Truck, Weighment


class WeighmentInline(admin.TabularInline):
    model = Weighment
    extra = 0
    readonly_fields = ("net_kg",)


@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ("name", "party_type", "phone", "city", "user")
    list_filter = ("party_type",)
    search_fields = ("name", "phone", "gst_no")


@admin.register(Truck)
class TruckAdmin(admin.ModelAdmin):
    list_display = ("number", "driver_name", "driver_phone")
    search_fields = ("number", "driver_name")


@admin.register(Consignment)
class ConsignmentAdmin(admin.ModelAdmin):
    list_display = ("id", "truck", "buyer", "wood_type", "status", "expected_arrival", "net_weight_kg")
    list_filter = ("status", "wood_type")
    search_fields = ("truck__number", "buyer__name")
    inlines = [WeighmentInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("buyer", "amount", "date", "mode", "reference")
    list_filter = ("mode",)
