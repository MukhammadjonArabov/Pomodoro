from django.shortcuts import render
from pomodoro.models import PomodoroSession
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth, TruncYear
from django.http import JsonResponse

def dashboard(request):
    user = request.user
    
    today = timezone.now().date()
    if user.is_authenticated:
        today_sessions = PomodoroSession.objects.filter(user=user, started_at__date=today, status='finished')
    else:
        today_sessions = PomodoroSession.objects.none()
    
    # Calculate today's training time in minutes
    today_training = today_sessions.aggregate(total=Sum('duration'))['total'] or 0
    
    # Calculate streak
    streak = 0
    current_date = today
    if user.is_authenticated:
        while True:
            if PomodoroSession.objects.filter(user=user, started_at__date=current_date, status='finished').exists():
                streak += 1
                current_date -= timedelta(days=1)
            else:
                if current_date == today:
                    current_date -= timedelta(days=1)
                    continue
                break

    # Check for 1-month expiration of Telegram verification
    auth_expired = False
    if user.is_authenticated:
        from users.models import TelegramVerification
        verification = TelegramVerification.objects.filter(
            telegram_id=user.profile.telegram_id,
            is_verified=True
        ).order_by('-created_at').first()
        
        if not verification or verification.is_expired:
            auth_expired = True
            # We don't necessarily logout, just prompt for new code as requested
            # But the user said "yana sayit kod so'rasin", which usually implies re-auth.
            # To be safe, we'll set auto_open_login to True.
    
    context = {
        'user': user,
        'telegram_id': user.profile.telegram_id if user.is_authenticated else None,
        'today_pomodoros': today_sessions.count(),
        'today_training': today_training,
        'streak': streak,
        'recent_sessions': PomodoroSession.objects.filter(user=user).order_by('-started_at')[:10] if user.is_authenticated else [],
        'auto_open_login': not user.is_authenticated or auth_expired
    }
    return render(request, 'dashboard/index.html', context)

def stats_index(request):
    user = User.objects.first()
    return render(request, 'stats/index.html', {'user': user, 'telegram_id': user.profile.telegram_id if user else None})

def api_stats_data(request):
    user = request.user if request.user.is_authenticated else User.objects.first()
    period = request.GET.get('period', 'week') # day, week, month, year
    
    now = timezone.now()
    if period == 'day':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        trunc_func = TruncDate # Using Date for now, could be TruncHour for better day view
    elif period == 'week':
        start_date = (now - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
        trunc_func = TruncDate
    elif period == 'month':
        start_date = (now - timedelta(days=29)).replace(hour=0, minute=0, second=0, microsecond=0)
        trunc_func = TruncDate
    elif period == 'year':
        start_date = (now - timedelta(days=364)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        trunc_func = TruncMonth
    else:
        start_date = now - timedelta(weeks=1)
        trunc_func = TruncDate

    sessions = PomodoroSession.objects.filter(
        user=user, 
        started_at__gte=start_date,
        status='finished'
    ).annotate(date=trunc_func('started_at')).values('date').annotate(
        total_focus=Sum('duration'),
        count=Count('id')
    ).order_by('date')

    labels = []
    focus_data_minutes = []
    sessions_data = []

    for entry in sessions:
        if period == 'year':
            label = entry['date'].strftime('%b %Y')
        else:
            label = entry['date'].strftime('%d %b')
        labels.append(label)
        focus_data_minutes.append(entry['total_focus'])
        sessions_data.append(entry['count'])

    # Convert to hours for axis charts
    focus_data_hours = [round(m / 60, 2) for m in focus_data_minutes]
    
    # Calculate percentages for doughnut chart (share of total focus time in period)
    total_focus_in_period = sum(focus_data_minutes)
    percentages = []
    if total_focus_in_period > 0:
        percentages = [round((m / total_focus_in_period) * 100, 1) for m in focus_data_minutes]

    return JsonResponse({
        'labels': labels,
        'focus_time': focus_data_hours, # Now in hours
        'sessions_count': sessions_data,
        'percentages': percentages
    })
