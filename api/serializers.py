from rest_framework import serializers
from transactions.models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'id', 'amount', 'transaction_type', 'payment_app',
            'merchant', 'category', 'date', 'upi_ref', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']