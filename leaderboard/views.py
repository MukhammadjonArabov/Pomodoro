from django.shortcuts import render
from stats.models import Statistic
from django.db.models import F

from django.db.models import Sum, Q

def leaderboard(request):
    # Filtering for users with at least 1 pomodoro and ordering by most pomodoros
    top_users = Statistic.objects.filter(total_pomodoros__gt=0).select_related('user', 'user__profile').annotate(
        calculated_time=Sum('user__pomodoro_sessions__duration', filter=Q(user__pomodoro_sessions__status='finished'))
    ).order_by('-total_pomodoros')[:50]
    return render(request, 'dashboard/leaderboard.html', {'top_users': top_users})
