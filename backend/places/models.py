from django.db import models
from django.utils import timezone


class Place(models.Model):
    address = models.CharField(
        'адрес',
        max_length=100,
        unique=True
    )
    lat = models.DecimalField(
        'широта',
        max_digits=9,
        decimal_places=2,
        blank=True,
        null=True
    )
    lon = models.DecimalField(
        'долгота',
        max_digits=9,
        decimal_places=2,
        blank=True,
        null=True
    )
    created_date = models.DateTimeField(
        'Дата запроса',
        default=timezone.now
    )

    class Meta:
        verbose_name = 'место'
        verbose_name_plural = 'места'

    def __str__(self):
        return self.address
