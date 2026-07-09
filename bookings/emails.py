from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse


def _format_date(value):
    return value.strftime("%Y-%m-%d") if hasattr(value, "strftime") else str(value)


def _format_time(value):
    return value.strftime("%I:%M %p") if hasattr(value, "strftime") else str(value)


def _booking_lines(booking):
    return [
        f"Client: {booking.full_name}",
        f"Email: {booking.email}",
        f"Phone: {booking.phone}",
        f"Service: {booking.service}",
        f"Session: {booking.session or 'Confirmed after consultation'}",
        f"Date: {booking.appointment_date:%B %d, %Y}",
        f"Time: {booking.appointment_time:%I:%M %p}",
        f"Payment method: {booking.get_payment_method_display()}",
        f"Payment status: {booking.get_payment_status_display()}",
        f"Booking status: {booking.get_status_display()}",
        f"Notes: {booking.notes or 'None'}",
    ]


def notify_manager_new_booking(request, booking):
    admin_url = request.build_absolute_uri(
        reverse("admin:bookings_booking_change", args=[booking.pk])
    )
    message = "\n".join(
        [
            "New Appointment Booking",
            f"Hello {getattr(settings, 'BOOKING_MANAGER_NAME', '')},",
            "",
            "A new appointment booking has been submitted through the Luxe Studio booking system.",
            "",
            "Client Information",
            f"Full Name: {booking.full_name}",
            f"First Name: {booking.first_name}",
            f"Last Name: {booking.last_name}",
            f"Email Address: {booking.email}",
            f"Reply Email: {booking.email}",
            f"Phone Number: {booking.phone}",
            "",
            "Appointment Details",
            f"Selected Service: {booking.service}",
            f"Appointment Date: {_format_date(booking.appointment_date)}",
            f"Appointment Time: {_format_time(booking.appointment_time)}",
            f"Session Details: {booking.session or 'Confirmed after consultation'}",
            "",
            "Client Notes",
            booking.notes or "None",
            "",
            "Payment Review",
            f"Payment Method: {booking.get_payment_method_display()}",
            f"Payment Status: {booking.get_payment_status_display()}",
            f"Booking Status: {booking.get_status_display()}",
            "",
            f"Review this booking in Django admin: {admin_url}",
        ]
    )
    send_mail(
        subject="New Appointment Booking",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.BOOKING_MANAGER_EMAIL],
        fail_silently=False,
    )


def notify_client_booking_approved(booking):
    message = "\n".join(
        [
            f"Hello {booking.first_name},",
            "",
            "Your Luxe Studio booking has been approved. Your payment has been confirmed by the studio.",
            "",
            *_booking_lines(booking),
            "",
            "Thank you for booking with Luxe Studio.",
        ]
    )
    send_mail(
        subject="Your Luxe Studio booking is approved",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[booking.email],
        fail_silently=False,
    )


def notify_manager_payment_confirmed(booking):
    message = "\n".join(
        [
            "Payment Confirmed",
            f"Hello {getattr(settings, 'BOOKING_MANAGER_NAME', '')},",
            "",
            "A booking payment has been confirmed and the booking has been approved.",
            "",
            "Client Information",
            f"Full Name: {booking.full_name}",
            f"Email Address: {booking.email}",
            f"Phone Number: {booking.phone}",
            "",
            "Appointment Details",
            f"Selected Service: {booking.service}",
            f"Appointment Date: {_format_date(booking.appointment_date)}",
            f"Appointment Time: {_format_time(booking.appointment_time)}",
            f"Session Details: {booking.session or 'Confirmed after consultation'}",
            "",
            "Payment Review",
            f"Payment Method: {booking.get_payment_method_display()}",
            f"Payment Status: {booking.get_payment_status_display()}",
            f"Booking Status: {booking.get_status_display()}",
        ]
    )
    send_mail(
        subject="Payment Confirmed - Booking Approved",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.BOOKING_MANAGER_EMAIL],
        fail_silently=False,
    )
