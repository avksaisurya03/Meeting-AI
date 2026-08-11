from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('analyze/', views.analyze_view, name='analyze'),
]
