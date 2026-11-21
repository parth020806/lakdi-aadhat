from django.contrib import messages
from django.shortcuts import redirect, render
from .forms import EnquiryForm
from .models import WoodRate


def home(request):
    rates = WoodRate.objects.filter(is_visible=True)
    return render(request, "core/home.html", {"rates": rates})


def contact(request):
    form = EnquiryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Thank you! We will call you shortly.")
        return redirect("contact")
    return render(request, "core/contact.html", {"form": form})
