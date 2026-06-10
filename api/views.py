from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from django.utils import timezone
from transactions.models import Transaction
from parsers.parser import parse_upi_sms
from .serializers import TransactionSerializer
import datetime

class TransactionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transactions = Transaction.objects.filter(user=request.user)
        
        # Optional filters
        payment_app = request.query_params.get('payment_app')
        transaction_type = request.query_params.get('transaction_type')
        if payment_app:
            transactions = transactions.filter(payment_app=payment_app)
        if transaction_type:
            transactions = transactions.filter(transaction_type=transaction_type)

        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ParseSMSView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        sms_text = request.data.get('sms_text', '').strip()
        if not sms_text:
            return Response({'error': 'sms_text is required'}, status=status.HTTP_400_BAD_REQUEST)

        parsed = parse_upi_sms(sms_text)

        if 'amount' not in parsed or 'transaction_type' not in parsed:
            return Response({'error': 'Could not parse this SMS'}, status=status.HTTP_400_BAD_REQUEST)

        date = parsed.get('date', datetime.datetime.now())
        if isinstance(date, datetime.datetime) and not date.tzinfo:
            from django.utils.timezone import make_aware
            date = make_aware(date)

        transaction = Transaction.objects.create(
            user=request.user,
            amount=parsed.get('amount'),
            transaction_type=parsed.get('transaction_type'),
            payment_app=parsed.get('payment_app', 'bank'),
            merchant=parsed.get('merchant', ''),
            upi_ref=parsed.get('upi_ref', ''),
            raw_sms=parsed.get('raw_sms', ''),
            date=date,
            category=parsed.get('category', ''),
        )
        serializer = TransactionSerializer(transaction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_start = (this_month_start - timezone.timedelta(days=1)).replace(day=1)

        all_debits = Transaction.objects.filter(user=request.user, transaction_type='debit')

        this_month = all_debits.filter(date__gte=this_month_start).aggregate(Sum('amount'))['amount__sum'] or 0
        last_month = all_debits.filter(date__gte=last_month_start, date__lt=this_month_start).aggregate(Sum('amount'))['amount__sum'] or 0

        by_app = list(all_debits.values('payment_app').annotate(total=Sum('amount')).order_by('-total'))

        return Response({
            'this_month_total': this_month,
            'last_month_total': last_month,
            'total_transactions': Transaction.objects.filter(user=request.user).count(),
            'spending_by_app': by_app,
        })