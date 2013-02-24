from django.db import models

class Recap(models.Model):
    html = models.TextField()
    css = models.TextField()
    home_abbr = models.CharField(max_length=100)
    away_abbr = models.CharField(max_length=100)
    home_name = models.CharField(max_length=100)
    away_name = models.CharField(max_length=100)
    home_score = models.CharField(max_length=100)
    away_score = models.CharField(max_length=100)
