from datetime import time

from django.db import migrations


def create_opening_sessions(apps, schema_editor):
    OpeningSession = apps.get_model("bookings", "OpeningSession")
    defaults = [
        ("Monday-Saturday", time(9, 0), time(21, 0), 1),
        ("Sunday", time(11, 0), time(21, 0), 2),
    ]
    for day_range, opens_at, closes_at, display_order in defaults:
        OpeningSession.objects.get_or_create(
            day_range=day_range,
            defaults={
                "opens_at": opens_at,
                "closes_at": closes_at,
                "display_order": display_order,
            },
        )


def remove_opening_sessions(apps, schema_editor):
    OpeningSession = apps.get_model("bookings", "OpeningSession")
    OpeningSession.objects.filter(day_range__in=["Monday-Saturday", "Sunday"]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("bookings", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_opening_sessions, remove_opening_sessions),
    ]
