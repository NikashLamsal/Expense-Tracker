from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone
from datetime import timedelta
# Create your models here.


class CurrentBalance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    current_balance = models.FloatField(default = 0)

class Category(models.Model):
    CATEGORY_TYPES = [
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, default='fa-circle')
    color = models.CharField(max_length=7, default='#3b82f6')
    type = models.CharField(max_length=10, choices=CATEGORY_TYPES)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name

class TrackingHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  

    current_balance = models.ForeignKey(CurrentBalance , on_delete= models.CASCADE)
    amount = models.FloatField()
    description = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    # created_at = models.DateTimeField(auto_now_add=True)
    expense_type = models.CharField(choices = (('CREDIT','CREDIT'),('DEBIT', 'DEBIT')),max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)  # ADD THIS LINE


class EmailVerificationToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_valid(self):
        expiration_time = self.created_at + timedelta(hours=24)
        return timezone.now() < expiration_time
