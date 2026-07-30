import os
import json
import requests
from io import BytesIO
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib import messages
from django.urls import reverse
from xhtml2pdf import pisa
from .models import PreOrder, BatchMetric

# 🔑 Reads from Render environment variables in production, falls back to local test key
PAYSTACK_SECRET_KEY = os.environ.get(
    "PAYSTACK_SECRET_KEY", 
    "sk_test_0a4180007b1451128c9b7553529c94d437ff0648"
)

def home(request):
    metric = BatchMetric.objects.first()
    
    # Calculate progress percentage safely without crashing if metric is None
    if metric and metric.total_weeks:
        progress_percent = int((metric.current_week / metric.total_weeks) * 100)
    else:
        progress_percent = 57

    if request.method == "POST":
        buyer_name = request.POST.get("buyer_name")
        phone_number = request.POST.get("phone_number")
        quantity_str = request.POST.get("quantity", "50")
        notes = request.POST.get("notes", "")

        try:
            quantity = int(quantity_str)
        except ValueError:
            quantity = 50

        # Calculate deposit amount (e.g., GHS 10 per bird deposit)
        deposit_amount_ghs = quantity * 10 

        # 1. Save pending order to Database
        order = PreOrder.objects.create(
            buyer_name=buyer_name,
            phone_number=phone_number,
            quantity=quantity,
            notes=notes,
            amount_paid=deposit_amount_ghs,
            payment_status="PENDING"
        )

        # 2. Dynamically build callback URL (works on localhost AND live Render URL)
        callback_url = request.build_absolute_uri(
            reverse('verify_payment', kwargs={'order_id': order.id})
        )

        # 3. Initialize Paystack Mobile Money Transaction
        paystack_url = "https://api.paystack.co/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        
        # Paystack expects amount in pesewas (1 GHS = 100 pesewas)
        payload = {
            "email": f"buyer_{order.id}@legonpoultry.com",  # Placeholder email for MoMo
            "amount": int(deposit_amount_ghs * 100),
            "currency": "GHS",
            "callback_url": callback_url,
            "metadata": {
                "buyer_name": buyer_name,
                "phone_number": phone_number,
                "order_id": order.id
            }
        }

        try:
            response = requests.post(paystack_url, headers=headers, json=payload, timeout=10)
            res_data = response.json()
            
            if res_data.get("status"):
                order.paystack_ref = res_data["data"]["reference"]
                order.save()
                # Redirect buyer to Paystack MoMo Payment Page
                return redirect(res_data["data"]["authorization_url"])
            else:
                messages.error(request, f"Paystack Error: {res_data.get('message', 'Failed to initialize payment.')}")
        except Exception as e:
            messages.error(request, f"MoMo Gateway Connection Error: {str(e)}")

        return redirect("home")

    context = {
        "metric": metric,
        "progress_percent": progress_percent
    }
    return render(request, "index.html", context)


# --- PAYSTACK MOMO VERIFICATION VIEW ---
def verify_payment(request, order_id):
    order = get_object_or_404(PreOrder, id=order_id)
    reference = request.GET.get('reference')

    if reference:
        paystack_url = f"https://api.paystack.co/transaction/verify/{reference}"
        headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
        
        try:
            response = requests.get(paystack_url, headers=headers, timeout=10)
            res_data = response.json()

            if res_data.get("status") and res_data["data"]["status"] == "success":
                order.payment_status = "PAID"
                order.save()
                messages.success(request, f"🎉 Payment Successful! GHS {order.amount_paid} received via Mobile Money for Order #{order.id}.")
            else:
                order.payment_status = "FAILED"
                order.save()
                messages.error(request, "Mobile Money payment verification failed or was canceled.")
        except Exception as e:
            messages.error(request, f"Verification Error: {str(e)}")

    return redirect("home")


# --- PDF GENERATOR VIEW ---
def generate_pdf_report(request):
    metric = BatchMetric.objects.first()
    html_string = render_to_string('pdf_report.html', {'metric': metric})
    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html_string, dest=pdf_buffer)
    
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
    
    pdf_data = pdf_buffer.getvalue()
    pdf_buffer.close()

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="UG_Legon_Poultry_Proposal.pdf"'
    return response