from django.db import models

# Create your models here.
class School(models.Model):
    name = models.CharField(max_length=50, help_text='Enter the name of the school', unique=True, blank=False,
                            null=False)
    address = models.CharField(max_length=50, help_text='Enter the name of the school', blank=True, null=True)
    abbreviation = models.CharField(max_length=4, default=" ", help_text=' Enter the abbreviation for this school')
    ordering = ['name']

    def __str__(self):
        return self.name
