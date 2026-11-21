from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Sum


class Party(models.Model):
    TYPE_CHOICES = [("BUYER", "Buyer (Plywood factory)"), ("SUPPLIER", "Supplier (UP)")]
    name = models.CharField(max_length=120)
    party_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    gst_no = models.CharField("GST number", max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=60, blank=True)
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        help_text="Link a portal login so this buyer can see their own trucks and bills",
    )

    class Meta:
        verbose_name_plural = "parties"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_party_type_display()})"

    @property
    def total_billed(self):
        return sum((c.amount for c in self.purchases.all()), Decimal("0"))

    @property
    def total_paid(self):
        return self.payments.aggregate(t=Sum("amount"))["t"] or Decimal("0")

    @property
    def outstanding(self):
        return self.total_billed - self.total_paid


class Truck(models.Model):
    number = models.CharField(max_length=20, unique=True, help_text="e.g. UP14 AB 1234")
    driver_name = models.CharField(max_length=100, blank=True)
    driver_phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.number

    def save(self, *args, **kwargs):
        self.number = self.number.upper().strip()
        super().save(*args, **kwargs)


class Consignment(models.Model):
    """One truck load: from a UP supplier to a Yamunanagar buyer."""
    STATUS_CHOICES = [
        ("DISPATCHED", "Dispatched from UP"),
        ("IN_TRANSIT", "On the way"),
        ("ARRIVED", "Arrived at Yamunanagar"),
        ("UNLOADED", "Unloaded"),
        ("CANCELLED", "Cancelled"),
    ]
    truck = models.ForeignKey(Truck, on_delete=models.PROTECT, related_name="consignments")
    supplier = models.ForeignKey(
        Party, on_delete=models.PROTECT, related_name="supplies",
        limit_choices_to={"party_type": "SUPPLIER"}, null=True, blank=True,
    )
    buyer = models.ForeignKey(
        Party, on_delete=models.PROTECT, related_name="purchases",
        limit_choices_to={"party_type": "BUYER"},
    )
    wood_type = models.CharField(max_length=80, help_text="e.g. Poplar, Eucalyptus")
    origin = models.CharField("Loaded from (UP town)", max_length=80, blank=True)
    dispatched_on = models.DateField(null=True, blank=True)
    expected_arrival = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="DISPATCHED")
    rate_per_quintal = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"#{self.pk} {self.truck} -> {self.buyer.name}"

    @property
    def net_weight_kg(self):
        return self.weighments.aggregate(t=Sum("net_kg"))["t"] or Decimal("0")

    @property
    def net_quintal(self):
        return self.net_weight_kg / Decimal("100")

    @property
    def amount(self):
        return (self.net_quintal * self.rate_per_quintal).quantize(Decimal("0.01"))

    @property
    def paid(self):
        return self.payments.aggregate(t=Sum("amount"))["t"] or Decimal("0")


class Weighment(models.Model):
    """Dharam kanta entry. Net = gross - tare. A truck may be weighed more than once."""
    consignment = models.ForeignKey(Consignment, on_delete=models.CASCADE, related_name="weighments")
    gross_kg = models.DecimalField(max_digits=9, decimal_places=2)
    tare_kg = models.DecimalField(max_digits=9, decimal_places=2)
    net_kg = models.DecimalField(max_digits=9, decimal_places=2, editable=False)
    slip_photo = models.ImageField(upload_to="slips/", blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        self.net_kg = self.gross_kg - self.tare_kg
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.consignment} - {self.net_kg} kg"


class Payment(models.Model):
    MODE_CHOICES = [("CASH", "Cash"), ("UPI", "UPI"), ("CHEQUE", "Cheque"), ("BANK", "Bank transfer")]
    buyer = models.ForeignKey(Party, on_delete=models.PROTECT, related_name="payments",
                              limit_choices_to={"party_type": "BUYER"})
    consignment = models.ForeignKey(Consignment, null=True, blank=True, on_delete=models.SET_NULL,
                                    related_name="payments")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    mode = models.CharField(max_length=8, choices=MODE_CHOICES, default="CASH")
    reference = models.CharField(max_length=60, blank=True, help_text="Cheque no. / UTR")

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.buyer.name} paid Rs {self.amount} on {self.date}"
