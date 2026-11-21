from django.conf import settings
from django.db import models


class Profile(models.Model):
    ROLE_CHOICES = [
        ("OWNER", "Owner"),
        ("STAFF", "Staff"),
        ("BUYER", "Buyer (Factory)"),
        ("SUPPLIER", "Supplier"),
    ]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="BUYER")
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=120, blank=True)
    is_approved = models.BooleanField(default=False, help_text="Tick to let this user into the portal")

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    @property
    def is_internal(self):
        return self.role in ("OWNER", "STAFF")
