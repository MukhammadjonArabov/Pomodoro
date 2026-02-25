from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User as AuthUser
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    LANGUAGE_CHOICES = [
        ('uz', 'O\'zbek'),
        ('en', 'English'),
        ('ru', 'Русский'),
    ]
    
    user = models.OneToOneField(AuthUser, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='uz')
    birth_date = models.DateField(null=True, blank=True)
    occupation = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

@receiver(post_save, sender=AuthUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=AuthUser)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class LegacyUser(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    full_name = models.CharField(max_length=255)
    language = models.CharField(max_length=2, default='uz')
    birth_date = models.DateField(null=True, blank=True)
    occupation = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name or str(self.telegram_id)

class TelegramVerification(models.Model):
    telegram_id = models.BigIntegerField()
    phone_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=150, null=True, blank=True)
    last_name = models.CharField(max_length=150, null=True, blank=True)
    code = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    @property
    def is_expired(self):
        from django.utils import timezone
        from datetime import timedelta
        return timezone.now() > self.created_at + timedelta(days=30)

    def __str__(self):
        return f"{self.telegram_id} - {self.code}"
