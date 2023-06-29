from django.db import models

# Create your models here.

# adminapp/models.py

class QueryResult(models.Model):
    headings = models.CharField(max_length=255)
    short_description = models.TextField()
    url = models.URLField()

    def __str__(self):
        return self.headings
