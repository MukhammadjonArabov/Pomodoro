from django.db import models
from django.contrib.auth.models import User

class Statistic(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='statistics')
    total_pomodoros = models.IntegerField(default=0)
    total_training_time = models.IntegerField(default=0, help_text="Total time in minutes")
    streak = models.IntegerField(default=0)
    last_active = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Stats for {self.user.username}"
