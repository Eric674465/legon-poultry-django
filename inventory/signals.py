from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import DailyLog, FeedStock

@receiver(post_save, sender=DailyLog)
def deduct_feed_on_daily_log(sender, instance, created, **kwargs):
    """
    Automatically deducts feed bags from FeedStock 
    whenever a farm worker saves a DailyLog.
    """
    if created:
        # Deduct used feed bags from starter/grower/finisher stock
        feed_item = FeedStock.objects.first()  # Or match specific feed type
        if feed_item:
            feed_item.bags_in_stock -= int(instance.feed_consumed_bags)
            if feed_item.bags_in_stock < 0:
                feed_item.bags_in_stock = 0
            feed_item.save()