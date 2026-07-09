from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from .emails import notify_manager_new_booking
from .forms import BookingForm
from .models import Booking, OpeningSession


def home(request):
    opening_sessions = OpeningSession.objects.all()
    return render(
        request,
        "bookings/home.html",
        {"opening_sessions": opening_sessions},
    )


@require_POST
def create_booking(request):
    form = BookingForm(request.POST)

    if not form.is_valid():
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"errors": form.errors}, status=400)
        messages.error(request, "Please check the booking details and try again.")
        return redirect("home")

    booking = form.save()
    notify_manager_new_booking(request, booking)
    payload = {
        "id": booking.id,
        "fullName": booking.full_name,
        "service": booking.service,
        "date": booking.appointment_date.isoformat(),
        "time": booking.appointment_time.strftime("%H:%M"),
        "session": booking.session or "Confirmed after consultation",
        "status": booking.get_status_display(),
        "paymentStatus": booking.get_payment_status_display(),
    }

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"booking": payload}, status=201)

    messages.success(
        request,
        "Booking submitted. It will be confirmed after payment is verified by the manager.",
    )
    return redirect("home")


@require_POST
def update_payment_method(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    payment_method = request.POST.get("payment_method", "")
    valid_methods = {choice for choice, label in Booking.PaymentMethod.choices}

    if payment_method not in valid_methods or payment_method == "":
        return JsonResponse(
            {"error": "Please choose a valid payment method."},
            status=400,
        )

    booking.payment_method = payment_method
    booking.save(update_fields=["payment_method", "updated_at"])
    return JsonResponse(
        {
            "paymentMethod": booking.payment_method,
            "paymentMethodDisplay": booking.get_payment_method_display(),
        }
    )


@require_GET
def booked_slots(request):
    bookings = Booking.objects.filter(
        status__in=[Booking.BookingStatus.PENDING, Booking.BookingStatus.APPROVED]
    )
    selected_date = request.GET.get("date")
    if selected_date:
        bookings = bookings.filter(appointment_date=selected_date)

    return JsonResponse(
        {
            "booked_slots": [
                {
                    "date": booking.appointment_date.isoformat(),
                    "time": booking.appointment_time.strftime("%H:%M"),
                }
                for booking in bookings
            ]
        }
    )
