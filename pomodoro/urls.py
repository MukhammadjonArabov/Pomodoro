from django.urls import path
from . import views

urlpatterns = [
    path('start/', views.start_session, name='start_session'),
    path('stop/<int:pk>/', views.stop_session, name='stop_session'),
]
