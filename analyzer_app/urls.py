from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('analyze/', views.analyze_view, name='analyze'),
    path('meeting/<uuid:meeting_id>/', views.meeting_detail_view, name='meeting_detail'),
]
