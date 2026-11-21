from django.contrib import messages
from django.shortcuts import redirect, render
from .forms import SignUpForm


def signup(request):
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Registered! You can log in once the owner approves your account.")
        return redirect("login")
    return render(request, "registration/signup.html", {"form": form})


def pending(request):
    return render(request, "registration/pending.html")
