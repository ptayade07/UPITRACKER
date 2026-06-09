from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['date', 'amount', 'transaction_type', 'payment_app', 'merchant', 'category']
    list_filter = ['transaction_type', 'payment_app', 'category']
    search_fields = ['merchant', 'upi_ref', 'raw_sms']