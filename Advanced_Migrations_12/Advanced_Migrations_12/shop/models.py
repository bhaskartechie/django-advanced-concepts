from django.db import models


class Client(models.Model):
    full_name = models.CharField(max_length=255)  # 🔧 renamed from 'name'
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True)  # 🔧 new

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
        constraints = [
            models.UniqueConstraint(
                fields=['email', 'phone_number'], name='unique_customer_email_phone'
            )
        ]


class Order(models.Model):
    customer = models.ForeignKey(Client, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['created_at'], name='order_created_idx')]
