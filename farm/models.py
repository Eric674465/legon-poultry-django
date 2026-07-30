from django.db import models

class PreOrder(models.Model):
    buyer_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20)
    quantity = models.IntegerField(default=50)
    notes = models.TextField(blank=True, null=True)
    
    # --- MoMo Payment Fields ---
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    paystack_ref = models.CharField(max_length=100, blank=True, null=True)
    payment_status = models.CharField(
        max_length=20, 
        choices=[('PENDING', 'Pending'), ('PAID', 'Paid'), ('FAILED', 'Failed')],
        default='PENDING'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.buyer_name} - {self.quantity} Birds ({self.payment_status})"

class BatchMetric(models.Model):
    batch_name = models.CharField(max_length=100, default="Batch #2026-A")
    current_week = models.IntegerField(default=4)
    total_weeks = models.IntegerField(default=7)
    flock_capacity = models.IntegerField(default=10000)
    target_weight = models.CharField(max_length=50, default="2.0 - 2.5 kg")
    mortality_count = models.IntegerField(default=35)

    def __str__(self):
        return self.batch_name
