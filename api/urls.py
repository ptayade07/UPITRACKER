from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    # Auth
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Transactions
    path('transactions/', views.TransactionListView.as_view(), name='api_transactions'),
    path('transactions/parse-sms/', views.ParseSMSView.as_view(), name='api_parse_sms'),

    # Dashboard
    path('dashboard/', views.DashboardView.as_view(), name='api_dashboard'),
]