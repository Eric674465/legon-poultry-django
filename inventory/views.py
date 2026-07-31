from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required  # 👈 Import login guard
from .models import FeedStock, DailyLog

@login_required(login_url='/admin/login/')  # 👈 Protects view from public access
def inventory_dashboard(request):
    logs = DailyLog.objects.all().order_by('-date')[:10]
    feed_stocks = FeedStock.objects.all()
    
    context = {
        'logs': logs,
        'feed_stocks': feed_stocks,
    }
    return render(request, 'inventory/dashboard.html', context)