from django.db import models
from farm.models import BatchMetric  # Connects directly to your farm batch

class FeedStock(models.Model):
    FEED_TYPES = [
        ('STARTER', 'Starter Crumble (Wks 1-2)'),
        ('GROWER', 'Grower Pellets (Wks 3-4)'),
        ('FINISHER', 'Finisher Pellets (Wks 5-7)'),
    ]
    feed_type = models.CharField(max_length=20, choices=FEED_TYPES)
    bags_in_stock = models.IntegerField(default=0)
    bag_weight_kg = models.DecimalField(max_digits=5, decimal_places=2, default=50.0)
    reorder_threshold = models.IntegerField(default=20, help_text="Minimum bag count before alert")
    cost_per_bag_ghs = models.DecimalField(max_digits=8, decimal_places=2)
    last_restocked = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_feed_type_display()} - {self.bags_in_stock} bags left"


class DailyLog(models.Model):
    batch = models.ForeignKey(BatchMetric, on_delete=models.CASCADE, related_name="daily_logs")
    date = models.DateField()
    feed_consumed_bags = models.DecimalField(max_digits=5, decimal_places=2)
    water_consumed_liters = models.DecimalField(max_digits=8, decimal_places=2)
    mortality_count = models.IntegerField(default=0, help_text="Number of dead birds today")
    culled_count = models.IntegerField(default=0, help_text="Sick/weak birds removed")
    average_weight_kg = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.batch.batch_name} Log - {self.date}"


class MedicalSupply(models.Model):
    item_name = models.CharField(max_length=100)  # e.g., Gumboro Vaccine, Vitamins
    category = models.CharField(max_length=50, choices=[('VACCINE', 'Vaccine'), ('ANTIBIOTIC', 'Antibiotic'), ('VITAMIN', 'Supplement')])
    quantity_available = models.IntegerField()
    unit = models.CharField(max_length=20, default="vials")  # vials, liters, sachets
    expiry_date = models.DateField()

    def __str__(self):
        return f"{self.item_name} ({self.quantity_available} {self.unit})"