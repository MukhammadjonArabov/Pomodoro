import random
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Profile, TelegramVerification
from django.contrib.auth import login

@api_view(['POST'])
@permission_classes([AllowAny])
def telegram_auth_callback(request):
    """
    Endpoint for the Telegram bot to register/update a user's phone number
    and generate a 4-digit verification code.
    """
    telegram_id = request.data.get('telegram_id')
    phone_number = request.data.get('phone_number')

    if not telegram_id or not phone_number:
        return Response({'error': 'Missing telegram_id or phone_number'}, status=status.HTTP_400_BAD_REQUEST)

    # Check for existing unexpired verification
    verification = TelegramVerification.objects.filter(telegram_id=telegram_id).first()
    
    if verification and not verification.is_expired:
        return Response({
            'code': verification.code,
            'is_new': False,
            'was_expired': False
        }, status=status.HTTP_200_OK)

    # If it exists but is expired, or if it doesn't exist, we need a new one
    was_expired = verification.is_expired if verification else False
    
    # Note: We delete any old entries to ensure fresh created_at and clean state
    TelegramVerification.objects.filter(telegram_id=telegram_id).delete()

    # Generate new 4-digit code
    code = f"{random.randint(1000, 9999)}"

    # Create new verification entry
    TelegramVerification.objects.create(
        telegram_id=telegram_id,
        phone_number=phone_number,
        code=code,
        is_verified=False
    )

    return Response({
        'code': code,
        'is_new': True,
        'was_expired': was_expired
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_telegram_code(request):
    """
    Endpoint for the website to verify the 4-digit code 
    and log the user in.
    """
    code = request.data.get('code')

    if not code:
        return Response({'error': 'Code is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        verification = TelegramVerification.objects.get(code=code)
        
        if verification.is_expired:
            return Response({'error': 'Code expired'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if user exists with this telegram_id or create one
        username = f"tg_{verification.telegram_id}"
        user, created = User.objects.get_or_create(username=username)
        
        # Update profile
        profile = user.profile
        profile.telegram_id = verification.telegram_id
        profile.phone_number = verification.phone_number
        profile.save()

        # Mark as verified (optional now since we reuse it, but good for tracking)
        if not verification.is_verified:
            verification.is_verified = True
            verification.save()

        # Log the user in
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        return Response({
            'success': True, 
            'username': user.username,
            'full_name': user.get_full_name() or user.username
        }, status=status.HTTP_200_OK)

    except TelegramVerification.DoesNotExist:
        return Response({'error': 'Invalid code'}, status=status.HTTP_400_BAD_REQUEST)
