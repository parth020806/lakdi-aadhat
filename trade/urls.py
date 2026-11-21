from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("trucks/", views.consignment_list, name="consignment_list"),
    path("trucks/new/", views.consignment_create, name="consignment_create"),
    path("trucks/<int:pk>/", views.consignment_detail, name="consignment_detail"),
    path("trucks/<int:pk>/weigh/", views.add_weighment, name="add_weighment"),
    path("trucks/<int:pk>/status/", views.update_status, name="update_status"),
    path("payments/new/", views.payment_create, name="payment_create"),
    path("ledger/<int:pk>/", views.ledger, name="ledger"),
]
