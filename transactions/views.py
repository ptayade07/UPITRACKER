from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Transaction

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