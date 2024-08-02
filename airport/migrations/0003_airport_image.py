# Generated by Django 5.0.7 on 2024-08-02 14:35

import airport.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("airport", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="airport",
            name="image",
            field=models.ImageField(
                null=True, upload_to=airport.models.create_custom_path
            ),
        ),
    ]