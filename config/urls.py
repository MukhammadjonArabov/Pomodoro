from django.contrib import admin
from django.urls import path, include
from stats import views as stats_views
from users import views as user_views
from leaderboard import views as leaderboard_views
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('users/', include('users.urls')),
    path('', stats_views.dashboard, name='dashboard'),
    path('leaderboard/', leaderboard_views.leaderboard, name='leaderboard'),
    path('stats/', include('stats.urls')),
    path('pomodoro/', include('pomodoro.urls')),
    path('profile/', user_views.profile_view, name='profile'),
    path('profile/<int:telegram_id>/', user_views.user_detail_view, name='user_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
