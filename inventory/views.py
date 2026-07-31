from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Sum
from .models import DailyLog, FeedStock, MedicalSupply
from farm.models import BatchMetric

def inventory_dashboard(request):
    active_batch = BatchMetric.objects.first()
    logs = DailyLog.objects.filter(batch=active_batch).order_by('-date') if active_batch else []
    
    # 1. Calculate Real-Time FCR Engine
    total_feed_bags = DailyLog.objects.filter(batch=active_batch).aggregate(Sum('feed_consumed_bags'))['feed_consumed_bags__sum'] or 0
    total_feed_kg = float(total_feed_bags) * 50.0  # 50kg per bag
    
    latest_log = logs.first()
    current_avg_weight = float(latest_log.average_weight_kg) if latest_log and latest_log.average_weight_kg else 0.0
    initial_birds = 10000  # Default batch capacity
    
    total_mortality = DailyLog.objects.filter(batch=active_batch).aggregate(Sum('mortality_count'))['mortality_count__sum'] or 0
    living_birds = initial_birds - total_mortality
    total_biomass_kg = living_birds * current_avg_weight

    # Formula: Total Feed Consumed (kg) / Total Flock Weight Gain (kg)
    fcr = round(total_feed_kg / total_biomass_kg, 2) if total_biomass_kg > 0 else 0.0

    # 2. Check Low-Stock Alerts
    feed_stocks = FeedStock.objects.all()
    low_stock_alerts = [item for item in feed_stocks if item.bags_in_stock <= item.reorder_threshold]

    # Handle Mobile Daily Log Form Submit
    if request.method == "POST":
        date = request.POST.get("date")
        feed_consumed_bags = request.POST.get("feed_consumed_bags")
        water_consumed_liters = request.POST.get("water_consumed_liters")
        mortality_count = request.POST.get("mortality_count")
        average_weight_kg = request.POST.get("average_weight_kg")
        notes = request.POST.get("notes")

        DailyLog.objects.create(
            batch=active_batch,
            date=date,
            feed_consumed_bags=feed_consumed_bags,
            water_consumed_liters=water_consumed_liters,
            mortality_count=mortality_count,
            average_weight_kg=average_weight_kg,
            notes=notes
        )
        messages.success(request, f"Daily log recorded for {date}!")
        return redirect("inventory_dashboard")

    context = {
        "active_batch": active_batch,
        "logs": logs[:7],  # Show last 7 days
        "fcr": fcr,
        "feed_stocks": feed_stocks,
        "low_stock_alerts": low_stock_alerts,
        "total_mortality": total_mortality,
    }
    return render(request, "inventory/dashboard.html", context)