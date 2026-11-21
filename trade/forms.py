from django import forms
from .models import Consignment, Payment, Truck, Weighment

DATE = forms.DateInput(attrs={"type": "date"})


class ConsignmentForm(forms.ModelForm):
    truck_number = forms.CharField(max_length=20, help_text="New numbers are created automatically")
    driver_name = forms.CharField(max_length=100, required=False)
    driver_phone = forms.CharField(max_length=20, required=False)

    class Meta:
        model = Consignment
        fields = ["supplier", "buyer", "wood_type", "origin", "dispatched_on",
                  "expected_arrival", "status", "rate_per_quintal", "notes"]
        widgets = {"dispatched_on": DATE, "expected_arrival": DATE, "notes": forms.Textarea(attrs={"rows": 2})}

    def save(self, commit=True):
        truck, _ = Truck.objects.get_or_create(number=self.cleaned_data["truck_number"].upper().strip())
        if self.cleaned_data["driver_name"]:
            truck.driver_name = self.cleaned_data["driver_name"]
        if self.cleaned_data["driver_phone"]:
            truck.driver_phone = self.cleaned_data["driver_phone"]
        truck.save()
        self.instance.truck = truck
        return super().save(commit)


class WeighmentForm(forms.ModelForm):
    class Meta:
        model = Weighment
        fields = ["gross_kg", "tare_kg", "slip_photo"]

    def clean(self):
        data = super().clean()
        g, t = data.get("gross_kg"), data.get("tare_kg")
        if g is not None and t is not None and t >= g:
            raise forms.ValidationError("Tare weight must be less than gross weight.")
        return data


class StatusForm(forms.ModelForm):
    class Meta:
        model = Consignment
        fields = ["status"]


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["buyer", "consignment", "amount", "date", "mode", "reference"]
        widgets = {"date": DATE}
