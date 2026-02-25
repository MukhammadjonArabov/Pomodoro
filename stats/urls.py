from django.urls import path

from . import views

urlpatterns = [
    path('', views.stats_index, name='stats_index'),
    path('data/', views.api_stats_data, name='api_stats_data'),
]
