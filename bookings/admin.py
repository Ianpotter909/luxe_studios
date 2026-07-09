from django.contrib import admin, messages

from .emails import notify_client_booking_approved, notify_manager_payment_confirmed
from .models import Booking, OpeningSession


@admin.action(description="Mark selected payments as confirmed")
def mark_payment_confirmed(modeladmin, request, queryset):
    updated = 0
    emailed = 0
    for booking in queryset:
        was_approved = booking.status == Booking.BookingStatus.APPROVED
        booking.payment_status = Booking.PaymentStatus.CONFIRMED
        booking.status = Booking.BookingStatus.APPROVED
        booking.save(update_fields=["payment_status", "status", "updated_at"])
        updated += 1
        if not was_approved:
            notify_client_booking_approved(booking)
            notify_manager_payment_confirmed(booking)
            emailed += 1
    messages.success(
        request,
        f"{updated} payment(s) confirmed and {emailed} approval email(s) sent.",
    )


@admin.action(description="Approve selected paid bookings")
def approve_paid_bookings(modeladmin, request, queryset):
    approved = 0
    skipped = 0
    for booking in queryset:
        was_approved = booking.status == Booking.BookingStatus.APPROVED
        if booking.approve_if_paid():
            approved += 1
            if not was_approved:
                notify_client_booking_approved(booking)
                notify_manager_payment_confirmed(booking)
        else:
            skipped += 1
    messages.success(request, f"{approved} booking(s) approved.")
    if skipped:
        messages.warning(
            request,
            f"{skipped} booking(s) were skipped because payment is not confirmed.",
        )


@admin.action(description="Cancel selected bookings")
def cancel_bookings(modeladmin, request, queryset):
    updated = queryset.update(status=Booking.BookingStatus.CANCELLED)
    messages.success(request, f"{updated} booking(s) cancelled.")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "service",
        "appointment_date",
        "appointment_time",
        "payment_method",
        "payment_status",
        "status",
        "created_at",
    )
    list_filter = (
        "status",
        "payment_status",
        "payment_method",
        "appointment_date",
        "service",
    )
    search_fields = ("first_name", "last_name", "email", "phone", "service")
    readonly_fields = ("created_at", "updated_at")
    actions = [mark_payment_confirmed, approve_paid_bookings, cancel_bookings]
    fieldsets = (
        (
            "Client",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "phone",
                )
            },
        ),
        (
            "Appointment",
            {
                "fields": (
                    "service",
                    "session",
                    "appointment_date",
                    "appointment_time",
                    "notes",
                )
            },
        ),
        (
            "Manager Review",
            {
                "fields": (
                    "payment_method",
                    "payment_status",
                    "status",
                    "admin_note",
                )
            },
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    def save_model(self, request, obj, form, change):
        was_approved = False
        if change:
            old_booking = Booking.objects.get(pk=obj.pk)
            was_approved = old_booking.status == Booking.BookingStatus.APPROVED

        if obj.payment_status == Booking.PaymentStatus.CONFIRMED:
            obj.status = Booking.BookingStatus.APPROVED

        super().save_model(request, obj, form, change)

        is_new_paid_approval = (
            obj.status == Booking.BookingStatus.APPROVED
            and obj.payment_status == Booking.PaymentStatus.CONFIRMED
            and not was_approved
        )
        if is_new_paid_approval:
            notify_client_booking_approved(obj)
            notify_manager_payment_confirmed(obj)


@admin.register(OpeningSession)
class OpeningSessionAdmin(admin.ModelAdmin):
    list_display = ("day_range", "opens_at", "closes_at", "display_order")
    list_editable = ("opens_at", "closes_at", "display_order")
