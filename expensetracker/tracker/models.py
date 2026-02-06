from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class CurrentBalance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    current_balance = models.FloatField(default = 0)

class TrackingHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  

    current_balance = models.ForeignKey(CurrentBalance , on_delete= models.CASCADE)
    amount = models.FloatField()
    description = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now=True)
    # created_at = models.DateTimeField(auto_now_add=True)
    expense_type = models.CharField(choices = (('CREDIT','CREDIT'),('DEBIT', 'DEBIT')),max_length=200)


