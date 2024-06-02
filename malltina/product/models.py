from django.db import models

class Product(models.Model):
    code = models.CharField(max_length=10, unique=True, db_index=True)
    name = models.CharField(max_length=255)  # db_index=True
    rating = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    avg_score = models.DecimalField(max_digits=2, decimal_places=1)
