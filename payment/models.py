from django.db import models
from django.db.models.fields.related import ForeignKey, OneToOneField
from app.models import *

# Create your models here.

class PaymentMethod(models.Model):  

    user = ForeignKey(Accounts, on_delete=models.CASCADE, blank=True, null=True)
    stripe_payment_method_id = models.CharField(max_length=100, blank=True)
    stripe_payment_method_response = models.JSONField(max_length=500, blank=True, null=True)

    pm_type = models.CharField(max_length=50, blank=True)
    name_on_card = models.CharField(max_length=100, blank=True)
    card_no = models.CharField(max_length=20, blank=True)
    exp_month = models.CharField(max_length=10, blank=True)
    exp_year = models.CharField(max_length=10, blank=True)
    cvv_no = models.CharField(max_length=10, blank=True)

    billing_address = models.TextField(max_length=1000, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=14, blank=True, null=True)
    currency = models.CharField(max_length=25, blank=True)
    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)





