from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from .models import Transaction
import json

@login_required
def transaction_list(request):
    transactions = Transaction.objects.filter(user=request.user)
    
    # Filters
    payment_app = request.GET.get('payment_app')
    transaction_type = request.GET.get('transaction_type')
    
    if payment_app:
        transactions = transactions.filter(payment_app=payment_app)
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    
    context = {
        'transactions': transactions,
        'payment_app': payment_app,
        'transaction_type': transaction_type,
    }
    return render(request, 'transactions/transaction_list.html', context)

@login_required
def dashboard(request):
    user = request.user
    now = timezone.now()
    
    # Current month and last month boundaries
    this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_start = (this_month_start - timezone.timedelta(days=1)).replace(day=1)

    all_debits = Transaction.objects.filter(user=user, transaction_type='debit')

    # This month vs last month
    this_month_total = all_debits.filter(date__gte=this_month_start).aggregate(Sum('amount'))['amount__sum'] or 0
    last_month_total = all_debits.filter(date__gte=last_month_start, date__lt=this_month_start).aggregate(Sum('amount'))['amount__sum'] or 0

    # Total transactions count
    total_transactions = Transaction.objects.filter(user=user).count()

    # Spending by payment app
    by_app = all_debits.values('payment_app').annotate(total=Sum('amount')).order_by('-total')
    app_labels = [item['payment_app'].upper() for item in by_app]
    app_data = [float(item['total']) for item in by_app]

    # Top 5 merchants
    top_merchants = (
        all_debits.exclude(merchant='')
        .values('merchant')
        .annotate(total=Sum('amount'))
        .order_by('-total')[:5]
    )

    # Monthly trend - last 6 months
    six_months_ago = now - timezone.timedelta(days=180)
    monthly = (
        all_debits.filter(date__gte=six_months_ago)
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )
    monthly_labels = [item['month'].strftime('%b %Y') for item in monthly]
    monthly_data = [float(item['total']) for item in monthly]

    context = {
        'this_month_total': this_month_total,
        'last_month_total': last_month_total,
        'total_transactions': total_transactions,
        'app_labels': json.dumps(app_labels),
        'app_data': json.dumps(app_data),
        'top_merchants': top_merchants,
        'monthly_labels': json.dumps(monthly_labels),
        'monthly_data': json.dumps(monthly_data),
    }
    return render(request, 'transactions/dashboard.html', context)