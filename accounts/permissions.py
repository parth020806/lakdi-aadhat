from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect


def approved_required(view):
    """Logged in AND approved by the owner."""
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        if not request.user.profile.is_approved:
            return redirect("pending")
        return view(request, *args, **kwargs)
    return wrapper


def internal_required(view):
    """Only Owner / Staff."""
    @wraps(view)
    @approved_required
    def wrapper(request, *args, **kwargs):
        if not request.user.profile.is_internal:
            messages.error(request, "Only staff can do that.")
            return redirect("dashboard")
        return view(request, *args, **kwargs)
    return wrapper
