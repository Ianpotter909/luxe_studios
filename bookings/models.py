from django.db import models
from django.utils import timezone


class Booking(models.Model):
    class PaymentMethod(models.TextChoices):
        NOT_SELECTED = "", "Not selected yet"
        CARD = "card", "Bank Card"
        TRANSFER = "transfer", "Bank Transfer"
        OTHER = "other", "Other Payment Option"

    class PaymentStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    class BookingStatus(models.TextChoices):
        PENDING = "pending", "Pending Approval"
        APPROVED = "approved", "Approved"
        CANCELLED = "cancelled", "Cancelled"

    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    email = models.EmailField()
    phone = models.CharField(max_length=40)
    service = models.CharField(max_length=160)
    session = models.CharField(max_length=160, blank=True)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.NOT_SELECTED,
        blank=True,
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    status = models.CharField(
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING,
    )
    notes = models.TextField(blank=True)
    admin_note = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["appointment_date", "appointment_time"],
                condition=models.Q(status__in=["pending", "approved"]),
                name="unique_active_booking_slot",
            )
        ]

    def __str__(self):
        return f"{self.full_name} - {self.service} on {self.appointment_date}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def approve_if_paid(self):
        if self.payment_status == self.PaymentStatus.CONFIRMED:
            self.status = self.BookingStatus.APPROVED
            self.save(update_fields=["status", "updated_at"])
            return True
        return False


class OpeningSession(models.Model):
    day_range = models.CharField(max_length=80)
    opens_at = models.TimeField()
    closes_at = models.TimeField()
    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "id"]

    def __str__(self):
        return f"{self.day_range}: {self.opens_at:%I:%M %p} - {self.closes_at:%I:%M %p}"
