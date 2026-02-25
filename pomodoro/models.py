from django.db import models
from django.contrib.auth.models import User

class PomodoroSession(models.Model):
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('finished', 'Finished'),
        ('paused', 'Paused'),
        ('stopped', 'Stopped'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pomodoro_sessions')
    duration = models.IntegerField(help_text="Duration in minutes")
    break_duration = models.IntegerField(default=5)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='running')
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.duration} min"
