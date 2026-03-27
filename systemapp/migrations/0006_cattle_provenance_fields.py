from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("systemapp", "0005_worker_login_photo"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="cattle",
            name="purchased_from_name",
            field=models.CharField(blank=True, default="", max_length=200),
        ),
        migrations.AddField(
            model_name="cattle",
            name="purchased_from_contact",
            field=models.CharField(blank=True, default="", max_length=50),
        ),
        migrations.AddField(
            model_name="cattle",
            name="purchased_from_location",
            field=models.CharField(blank=True, default="", max_length=200),
        ),
        migrations.AddField(
            model_name="cattle",
            name="purchased_from_address",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="cattle",
            name="purchase_notes",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="cattle",
            name="added_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="added_cattles",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="cattle",
            name="added_via",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
    ]

