from django.db import models

# Create your models here.
class Customization(models.Model):
    module_name = models.CharField(max_length=120)
    module_path = models.CharField(max_length=120)