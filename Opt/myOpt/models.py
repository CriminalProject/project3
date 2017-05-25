from django.db import models
from django.template.defaultfilters import default
from datetime import date
from unittest.util import _MAX_LENGTH

# Create your models here.

class OptimizationData(models.Model):
    date = models.DateField();
    store = models.CharField(max_length = 50)
    location = models.CharField(max_length = 100)
    code = models.IntegerField()
    salerProductName = models.CharField(max_length = 50)
    mainGroup = models.CharField(max_length = 50)
    subGroup = models.CharField(max_length = 50)
    productVariety = models.CharField(max_length = 50)
    salesAmount = models.IntegerField()
    
class FinalData(models.Model):
    date = models.DateField();
    salesAmount = models.IntegerField()
