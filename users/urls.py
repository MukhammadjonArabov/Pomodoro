from django.urls import path
from .views_api import telegram_auth_callback, verify_telegram_code

urlpatterns = [
    path('auth/telegram/callback/', telegram_auth_callback, name='telegram_auth_callback'),
    path('auth/telegram/verify/', verify_telegram_code, name='verify_telegram_code'),
]
