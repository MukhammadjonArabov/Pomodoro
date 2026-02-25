from django.shortcuts import render, redirect
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from pomodoro.models import PomodoroSession
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Profile

@login_required
def profile_view(request):
    user = request.user
    profile = user.profile
    
    if request.method == 'POST':
        new_name = request.POST.get('full_name')
        new_birth_date = request.POST.get('birth_date')
        new_occupation = request.POST.get('occupation')
        new_avatar = request.FILES.get('avatar')
        
        if new_name:
            # Handle name update (assuming first and last name split or just one)
            names = new_name.split(' ', 1)
            user.first_name = names[0]
            user.last_name = names[1] if len(names) > 1 else ''
            user.save()
            
        if new_birth_date:
            profile.birth_date = new_birth_date
        else:
            profile.birth_date = None
        if new_occupation:
            profile.occupation = new_occupation
        if new_avatar:
            profile.avatar = new_avatar
            
        profile.save()
        return redirect('profile')

    age = None
    if profile.birth_date:
        today = timezone.now().date()
        age = today.year - profile.birth_date.year - ((today.month, today.day) < (profile.birth_date.month, profile.birth_date.day))

    now = timezone.now()
    today_date = now.date()
    week_ago = (now - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
    month_ago = (now - timedelta(days=29)).replace(hour=0, minute=0, second=0, microsecond=0)
    year_ago = (now - timedelta(days=364)).replace(hour=0, minute=0, second=0, microsecond=0)

    stats = {
        'today': PomodoroSession.objects.filter(user=user, started_at__date=today_date, status='finished').count(),
        'week': PomodoroSession.objects.filter(user=user, started_at__gte=week_ago, status='finished').count(),
        'month': PomodoroSession.objects.filter(user=user, started_at__gte=month_ago, status='finished').count(),
        'year': PomodoroSession.objects.filter(user=user, started_at__gte=year_ago, status='finished').count(),
    }

    context = {
        'user': user,
        'profile': profile,
        'stats': stats,
        'age': age
    }
    return render(request, 'users/profile.html', context)

def user_detail_view(request, telegram_id):
    profile = Profile.objects.filter(telegram_id=telegram_id).first()
    if not profile:
        # Handle user not found
        return render(request, '404.html', status=404)
        
    user = profile.user
    age = None
    if profile.birth_date:
        today = timezone.now().date()
        age = today.year - profile.birth_date.year - ((today.month, today.day) < (profile.birth_date.month, profile.birth_date.day))

    # Calculate total focus hours for the public profile
    total_minutes = PomodoroSession.objects.filter(user=user, status='finished').aggregate(total=Sum('duration'))['total'] or 0
    total_hours = round(total_minutes / 60, 1)

    context = {
        'target_user': user,
        'age': age,
        'total_hours': total_hours
    }
    return render(request, 'users/public_profile.html', context)
