from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("systemapp", "0007_adminsettings"),
    ]

    operations = [
        migrations.CreateModel(
            name="PaymentSubmission",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("method", models.CharField(choices=[("UPI", "UPI"), ("BANK", "Bank Transfer")], default="UPI", max_length=20)),
                ("transaction_reference", models.CharField(blank=True, default="", max_length=120)),
                ("receipt", models.FileField(blank=True, null=True, upload_to="payment_receipts/")),
                ("status", models.CharField(choices=[("draft", "Draft"), ("submitted", "Submitted"), ("verified", "Verified"), ("rejected", "Rejected")], default="draft", max_length=20)),
                ("submitted_at", models.DateTimeField(blank=True, null=True)),
                ("verified_at", models.DateTimeField(blank=True, null=True)),
                ("admin_notes", models.TextField(blank=True, default="")),
                ("order", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="payment_submission", to="systemapp.order")),
            ],
        ),
    ]

