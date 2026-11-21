from django.db import models


class WoodRate(models.Model):
    """Daily rate shown on the public site. Update from admin."""
    wood_type = models.CharField(max_length=80)
    rate_per_quintal = models.DecimalField(max_digits=8, decimal_places=2)
    updated_on = models.DateField(auto_now=True)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ["wood_type"]

    def __str__(self):
        return f"{self.wood_type} - Rs {self.rate_per_quintal}/qtl"


class Enquiry(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    company = models.CharField(max_length=120, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    handled = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "enquiries"

    def __str__(self):
        return f"{self.name} ({self.phone})"
