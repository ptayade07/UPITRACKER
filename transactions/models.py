from django.db import models
from django.conf import settings

class Transaction(models.Model):

    DEBIT = 'debit'
    CREDIT = 'credit'
    TRANSACTION_TYPES = [(DEBIT, 'Debit'), (CREDIT, 'Credit')]

    GPAY = 'gpay'
    PHONEPE = 'phonepe'
    PAYTM = 'paytm'
    BANK = 'bank'
    PAYMENT_APPS = [
        (GPAY, 'Google Pay'),
        (PHONEPE, 'PhonePe'),
        (PAYTM, 'Paytm'),
        (BANK, 'Bank Transfer'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=6, choices=TRANSACTION_TYPES)
    payment_app = models.CharField(max_length=10, choices=PAYMENT_APPS, default=BANK)
    merchant = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=100, blank=True)
    note = models.TextField(blank=True)
    date = models.DateTimeField()
    upi_ref = models.CharField(max_length=50, blank=True)
    raw_sms = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.transaction_type} ₹{self.amount} via {self.payment_app} on {self.date.date()}"