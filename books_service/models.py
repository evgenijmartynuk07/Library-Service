from django.db import models


class Book(models.Model):
    COVER_CHOICES = (
        ("S", "SOFT"),
        ("H", "HARD"),
    )

    title = models.CharField(max_length=128)
    author = models.CharField(max_length=256)
    cover = models.CharField(max_length=8, choices=COVER_CHOICES)
    inventory = models.PositiveIntegerField(default=0)
    daily_fee = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self) -> str:
        return f"name: {self.title}, author: {self.author}"
