# Generated by Django 4.2.1 on 2023-05-06 08:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("books_service", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Borrowing",
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
                ("borrow_date", models.DateField(auto_now_add=True)),
                ("expected_return_date", models.DateField()),
                (
                    "actual_return_date",
                    models.DateField(blank=True, default=None, null=True),
                ),
                (
                    "book",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="borrowings",
                        to="books_service.book",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Payment",
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
                (
                    "status",
                    models.CharField(
                        choices=[("PENDING", "PENDING"), ("PAID", "PAID")],
                        default="PENDING",
                        max_length=32,
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[("PAYMENT", "PAYMENT"), ("FINE", "FINE")],
                        default="PAYMENT",
                        max_length=24,
                    ),
                ),
                ("session_url", models.URLField(blank=True, null=True)),
                ("session_id", models.CharField(blank=True, max_length=255, null=True)),
                ("money_to_pay", models.DecimalField(decimal_places=2, max_digits=8)),
                (
                    "borrowing",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payments",
                        to="borrowing_service.borrowing",
                    ),
                ),
            ],
        ),
    ]