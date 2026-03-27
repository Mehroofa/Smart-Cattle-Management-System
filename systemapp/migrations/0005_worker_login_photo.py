from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("systemapp", "0004_vetprofile_location"),
    ]

    operations = [
        migrations.AddField(
            model_name="worker_login",
            name="photo",
            field=models.ImageField(blank=True, null=True, upload_to="worker_photos/"),
        ),
    ]

