from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields.related import ForeignKey, OneToOneField



class Images(models.Model):
    license_no = models.CharField(max_length=12, null=True, blank=True)
    img = models.ImageField(upload_to='img/')

    def __str__(self):
        return str(self.id)



class Accounts(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=300, blank=True, null=True)
    email = models.CharField(max_length=300, blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    vehicle_no = models.CharField(max_length=30, blank=True, null=True)

    stripe_customer_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_customer_response = models.JSONField(max_length=1000, blank=True, null=True)


    def __str__(self):
        return self.name
    


class VehicleEntry(models.Model):
    user = ForeignKey(Accounts, on_delete=models.CASCADE, blank=True, null=True)
    slot_no = models.CharField(max_length=10, blank=True, null=True)
    entry = models.DateTimeField(auto_now_add=True)
    exit = models.DateTimeField(null=True, blank=True)
    fair = models.BigIntegerField(null=True, blank=True)
    # pending | completed 
    payment_status = models.CharField(max_length=25, null=True, blank=True)






