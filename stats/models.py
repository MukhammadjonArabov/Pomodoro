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

class FocusGameScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='focus_game_scores')
    score = models.IntegerField()
    accuracy = models.FloatField()
    reaction_speed = models.FloatField()
    max_combo = models.IntegerField()
    level = models.IntegerField()
    section = models.IntegerField()
    focus_index = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.section}-{self.level}: {self.score}"
