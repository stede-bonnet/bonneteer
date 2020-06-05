from django.db import models

# Create your models here.

class Searches(models.Model):
    name = models.CharField(max_length=128,default="")
    searches = models.IntegerField()

    def __str__(self):
        return self.name