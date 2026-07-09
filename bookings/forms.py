from django import forms
from django.utils import timezone

from .models import Booking


class BookingForm(forms.ModelForm):
    firstName = forms.CharField(max_length=80)
    lastName = forms.CharField(max_length=80)
    clientEmail = forms.EmailField()
    clientPhone = forms.CharField(max_length=40)
    appointmentDate = forms.DateField()
    appointmentTime = forms.TimeField()
    payment_method = forms.ChoiceField(
        choices=Booking.PaymentMethod.choices,
        required=False,
    )

    class Meta:
        model = Booking
        fields = [
            "service",
            "session",
            "payment_method",
            "notes",
        ]

    def clean_appointmentDate(self):
        appointment_date = self.cleaned_data["appointmentDate"]
        if appointment_date < timezone.localdate():
            raise forms.ValidationError("Please choose today or a future date.")
        return appointment_date

    def clean(self):
        cleaned_data = super().clean()
        appointment_date = cleaned_data.get("appointmentDate")
        appointment_time = cleaned_data.get("appointmentTime")

        if appointment_date and appointment_time:
            exists = Booking.objects.filter(
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                status__in=[
                    Booking.BookingStatus.PENDING,
                    Booking.BookingStatus.APPROVED,
                ],
            ).exists()
            if exists:
                raise forms.ValidationError(
                    "That time has already been booked. Please choose another slot."
                )

        return cleaned_data

    def save(self, commit=True):
        booking = super().save(commit=False)
        booking.first_name = self.cleaned_data["firstName"]
        booking.last_name = self.cleaned_data["lastName"]
        booking.email = self.cleaned_data["clientEmail"]
        booking.phone = self.cleaned_data["clientPhone"]
        booking.appointment_date = self.cleaned_data["appointmentDate"]
        booking.appointment_time = self.cleaned_data["appointmentTime"]
        if commit:
            booking.save()
        return booking
