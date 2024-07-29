from django.db import models
from users.models import School

class TestMaterialType(models.Model):
    NAME_CHOICES = [
        (1, 'Reusable Test Booklet'),
        (2, 'Answer Sheet'),
        (3, 'Admin Directions Booklet'),
        (4, 'Test Scoring'),
    ]
    name = models.IntegerField(choices=NAME_CHOICES, unique=True)
    price= models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Price")
    update=models.DateField(auto_now=True, verbose_name="Updated")

    def __str__(self):
        return f'{self.get_name_display()} - {self.price}'


class TestOrder(models.Model):
    school=models.ForeignKey(School, on_delete=models.CASCADE, related_name='orders')
    testing_dates=models.CharField(max_length=255, verbose_name="Testing dates")
    order_date=models.DateField(verbose_name="Order date")
    no_students_testing=models.PositiveSmallIntegerField(verbose_name="Number of students testing")
    sub_total=models.DecimalField(max_digits=6, decimal_places=2,verbose_name="Sub total")
    shipping=models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Shipping")
    total=models.DecimalField(max_digits=6, decimal_places=2,null=True, blank=True, verbose_name="Total")
    submitted=models.BooleanField(default=False, verbose_name="Submitted")
    finalized=models.BooleanField(default=False, verbose_name="Finalized")
    def __str__(self):
        return f'{self.school} - {self.order_date}'

LEVEL_CHOICES = [
        (8, 'Grade 3 without listening, Level 9'),
        (9, 'Grade 3 with listening, Level 9'),
        (10, 'Grade 4, Level 10'),
        (11, 'Grade 5, Level 11'),
        (12, 'Grade 6, Level 12'),
        (13, 'Grade 7, Level 13'),
        (14, 'Grade 8, Level 14'),
        (15, 'Grade 9, Level 15'),
        (16, 'Grade 10, Level 16'),
        (17, 'Grade 11-12, Level 17/18'),
    ]
class ReusableTestBookletOrdered(models.Model):
    order=models.ForeignKey(TestOrder, on_delete=models.CASCADE, related_name='test_booklets')
    level = models.IntegerField(choices=LEVEL_CHOICES, verbose_name="Level")
    count=models.PositiveSmallIntegerField(verbose_name="Count")

    def __str__(self):
        return f'{self.get_level_display()} - {self.count}'

class AnswerSheetOrdered(models.Model):
    order=models.ForeignKey(TestOrder, on_delete=models.CASCADE, related_name='answer_sheets')
    level = models.IntegerField(choices=LEVEL_CHOICES,  verbose_name="Level")
    count=models.PositiveSmallIntegerField( verbose_name="Count")
    def __str__(self):
        return f'{self.get_level_display()} - {self.count}'

DIRECTIONS_LEVEL_CHOICES = [
        (1, 'Grades 3-8, Level 9-14'),
        (2, 'Grades 9-12 , Level 15-17/18'),
    ]
class DirectionBookletOrdered(models.Model):
    order = models.ForeignKey(TestOrder, on_delete=models.CASCADE, related_name='direction_booklets')
    level = models.IntegerField(choices=DIRECTIONS_LEVEL_CHOICES, verbose_name="Direction")
    count = models.PositiveSmallIntegerField( verbose_name="Count")
    def __str__(self):
        return f'{self.get_level_display()} - {self.count}'
