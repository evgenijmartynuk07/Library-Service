# Generated by Django 4.2.1 on 2023-05-06 08:17

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Book",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=128)),
                ("author", models.CharField(max_length=256)),
                (
                    "cover",
                    models.CharField(
                        choices=[("S", "SOFT"), ("H", "HARD")], max_length=8
                    ),
                ),
                ("inventory", models.PositiveIntegerField(default=0)),
                ("daily_fee", models.DecimalField(decimal_places=2, max_digits=6)),
            ],
        ),
    ]
