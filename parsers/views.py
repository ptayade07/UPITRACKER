from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.timezone import make_aware
from django.contrib import messages
from transactions.models import Transaction
from .parser import parse_upi_sms
import datetime

@login_required
def upload_sms(request):
    if request.method == 'POST':
        sms_text = request.POST.get('sms_text', '').strip()
        if sms_text:
            parsed = parse_upi_sms(sms_text)

            if 'amount' not in parsed or 'transaction_type' not in parsed:
                messages.error(request, 'Could not parse this SMS. Please check the format.')
                return render(request, 'parsers/upload_sms.html')

            date = parsed.get('date', datetime.datetime.now())
            if not date.tzinfo:
                date = make_aware(date)

            Transaction.objects.create(
                user=request.user,
                amount=parsed.get('amount'),
                transaction_type=parsed.get('transaction_type'),
                payment_app=parsed.get('payment_app', 'bank'),
                merchant=parsed.get('merchant', ''),
                upi_ref=parsed.get('upi_ref', ''),
                raw_sms=parsed.get('raw_sms', ''),
                date=date,
            )
            messages.success(request, f"Transaction of ₹{parsed['amount']} saved successfully!")
            return redirect('upload_sms')

    return render(request, 'parsers/upload_sms.html')