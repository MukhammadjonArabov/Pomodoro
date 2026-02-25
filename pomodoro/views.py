from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
from .models import PomodoroSession
from django.contrib.auth.models import User
from stats.models import Statistic

@csrf_exempt
def start_session(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Auth required", "redirect": "/profile/"}, status=401)
        
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = request.user
            
            # Use custom duration if provided, otherwise default to 25
            duration = int(data.get('duration', 25))
                
            session = PomodoroSession.objects.create(
                user=user,
                duration=duration,
                break_duration=data.get('break_duration', 5),
                status='running'
            )
            return JsonResponse({
                "id": session.id,
                "status": session.status,
                "duration": session.duration
            })
        except (ValueError, TypeError, json.JSONDecodeError):
            return JsonResponse({"error": "Invalid data"}, status=400)
    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
def stop_session(request, pk):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            status_input = data.get('status', 'finished')
        except json.JSONDecodeError:
            status_input = 'finished'

        session = PomodoroSession.objects.filter(id=pk).first()
        if not session:
            return JsonResponse({"error": "Session not found"}, status=404)
            
        if session.status in ['finished', 'stopped']:
            return JsonResponse({"error": "Already completed"}, status=400)
            
        session.status = status_input
        session.finished_at = timezone.now()
        session.save()
        
        # Only update statistics if finished or if it's a stop with significant progress?
        # User said: "if finished ... if not finished stopped". 
        # "Total time adds regardless. Pomodoros = duration // 25"
        
        stats, created = Statistic.objects.get_or_create(user=session.user)
        
        if status_input == 'finished':
            # Add pomodoros based on duration (1 pomodoro per 25 mins)
            pomodoros_to_add = max(1, session.duration // 25)
            stats.total_pomodoros += pomodoros_to_add
            stats.total_training_time += session.duration
        else:
            # If stopped manually, we still add training time? 
            # User said: "Umumiy mashg'ulot vaqti ham agar user vaqtni o'zgartirsa shunga qarab qo'shilsin"
            # I interpret this as adding the full duration if finished, 
            # or maybe the elapsed time? But sessions only store 'duration' (planned).
            # For 'stopped' sessions, maybe we don't add pomodoros but add duration?
            # Actually, the user says "eng ko'p pamidor tepa qismida...". 
            # Let's add training time only for finished/significant progress.
            # But the prompt says "Umumiy mashg'ulot vaqti ham agar user vaqtni o'zgartirsa shunga qarab qo'shilsin"
            # Let's just follow the "duration // 25" for finished sessions.
            # For stopped, we add training time but NO pomodoros.
            stats.total_training_time += session.duration
            
        stats.save()
        
        return JsonResponse({"status": session.status})
    return JsonResponse({"error": "Method not allowed"}, status=405)
