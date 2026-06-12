from django.urls import path
from . import views

urlpatterns = [
    path('', views.ai_tools_home, name='ai_tools'),
    path('form-assistant/', views.form_assistant, name='form_assistant'),
    path('analyze-jd/', views.analyze_jd, name='analyze_jd'),
    path('interview-prep/', views.interview_prep, name='interview_prep'),
    path('follow-up-email/', views.follow_up_email, name='follow_up_email'),
]
