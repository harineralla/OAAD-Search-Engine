from django.db import models
import random

# Create your models here.

# adminapp/models.py


class QueryResult(models.Model):
    headlines = models.CharField(max_length=255)
    short_description = models.TextField()
    url = models.URLField()
    access_frequency = models.PositiveIntegerField(default=random.randint(1,10))  # Add the access frequency field
    payment = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Add the payment field

    def increment_access_frequency(self):
        self.access_frequency += 1
        self.save()

    def set_payment_details(self, payment_amount):
        self.payment = payment_amount
        self.save()

