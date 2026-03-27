from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("systemapp", "0006_cattle_provenance_fields"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AdminSettings",
            fields=[
                ("id", models.PositiveSmallIntegerField(default=1, editable=False, primary_key=True, serialize=False)),
                ("payee_name", models.CharField(blank=True, default="", max_length=200)),
                ("upi_id", models.CharField(blank=True, default="", max_length=200)),
                ("currency", models.CharField(blank=True, default="INR", max_length=10)),
                ("bank_name", models.CharField(blank=True, default="", max_length=200)),
                ("bank_account_number", models.CharField(blank=True, default="", max_length=50)),
                ("bank_ifsc", models.CharField(blank=True, default="", max_length=50)),
                ("support_email", models.EmailField(blank=True, default="", max_length=254)),
                ("support_phone", models.CharField(blank=True, default="", max_length=50)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="admin_settings_updates",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]

