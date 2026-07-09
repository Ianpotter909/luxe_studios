from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("bookings/create/", views.create_booking, name="create_booking"),
    path(
        "bookings/<int:booking_id>/payment-method/",
        views.update_payment_method,
        name="update_payment_method",
    ),
    path("bookings/slots/", views.booked_slots, name="booked_slots"),
]
