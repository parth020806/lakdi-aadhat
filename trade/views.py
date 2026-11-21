from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.permissions import approved_required, internal_required
from .forms import ConsignmentForm, PaymentForm, StatusForm, WeighmentForm
from .models import Consignment, Party


def _visible_consignments(user):
    qs = Consignment.objects.select_related("truck", "buyer", "supplier")
    if user.profile.is_internal:
        return qs
    return qs.filter(buyer__user=user)  # buyers only see their own trucks


@approved_required
def dashboard(request):
    qs = _visible_consignments(request.user)
    ctx = {
        "on_the_way": qs.filter(status__in=["DISPATCHED", "IN_TRANSIT"]),
        "arrived": qs.filter(status="ARRIVED"),
        "recent": qs.filter(status="UNLOADED")[:10],
    }
    if request.user.profile.is_internal:
        ctx["parties_due"] = sorted(
            Party.objects.filter(party_type="BUYER"), key=lambda p: p.outstanding, reverse=True
        )[:10]
    else:
        ctx["my_party"] = Party.objects.filter(user=request.user).first()
    return render(request, "trade/dashboard.html", ctx)


@approved_required
def consignment_list(request):
    qs = _visible_consignments(request.user)
    status = request.GET.get("status")
    if status:
        qs = qs.filter(status=status)
    return render(request, "trade/consignment_list.html",
                  {"consignments": qs, "status_choices": Consignment.STATUS_CHOICES})


@approved_required
def consignment_detail(request, pk):
    c = get_object_or_404(_visible_consignments(request.user), pk=pk)
    return render(request, "trade/consignment_detail.html", {
        "c": c,
        "weighment_form": WeighmentForm(),
        "status_form": StatusForm(instance=c),
    })


@internal_required
def consignment_create(request):
    form = ConsignmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        c = form.save()
        messages.success(request, "Truck added.")
        return redirect("consignment_detail", pk=c.pk)
    return render(request, "trade/form.html", {"form": form, "title": "Add truck / consignment"})


@internal_required
def add_weighment(request, pk):
    c = get_object_or_404(Consignment, pk=pk)
    form = WeighmentForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        w = form.save(commit=False)
        w.consignment = c
        w.recorded_by = request.user
        w.save()
        messages.success(request, f"Weighment saved: net {w.net_kg} kg")
    elif request.method == "POST":
        messages.error(request, "; ".join(sum(form.errors.values(), [])))
    return redirect("consignment_detail", pk=pk)


@internal_required
def update_status(request, pk):
    c = get_object_or_404(Consignment, pk=pk)
    form = StatusForm(request.POST or None, instance=c)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Status updated.")
    return redirect("consignment_detail", pk=pk)


@internal_required
def payment_create(request):
    form = PaymentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Payment recorded.")
        return redirect("dashboard")
    return render(request, "trade/form.html", {"form": form, "title": "Record payment"})


@approved_required
def ledger(request, pk):
    party = get_object_or_404(Party, pk=pk, party_type="BUYER")
    if not request.user.profile.is_internal and party.user_id != request.user.id:
        return redirect("dashboard")
    return render(request, "trade/ledger.html", {
        "party": party,
        "consignments": party.purchases.all(),
        "payments": party.payments.all(),
    })
