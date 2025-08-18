from django.db import models
from django.contrib.contenttypes.fields import GenericRelation


class ServiceType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)


class Service(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=False)
    comments = GenericRelation('comments.Comment')
    ratings = GenericRelation('ratings.Rating')


class ServiceProvider(models.Model):
    name = models.CharField(max_length=255)
    contact_email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    service = models.ManyToManyField(Service)
