from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    company = forms.CharField(max_length=120, label="Factory / Company name")
    phone = forms.CharField(max_length=20)

    class Meta:
        model = User
        fields = ("username", "first_name", "company", "phone")

    def save(self, commit=True):
        user = super().save(commit)
        if commit:
            p = user.profile
            p.company = self.cleaned_data["company"]
            p.phone = self.cleaned_data["phone"]
            p.save()
        return user
