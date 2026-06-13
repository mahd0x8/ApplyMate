from django.urls import path
from . import views

urlpatterns = [
    path('', views.profile_view, name='profile'),
    path('update/', views.profile_update, name='profile_update'),
    path('experience/add/', views.add_work_experience, name='add_work_experience'),
    path('experience/<int:pk>/delete/', views.delete_work_experience, name='delete_work_experience'),
    path('education/add/', views.add_education, name='add_education'),
    path('education/<int:pk>/delete/', views.delete_education, name='delete_education'),
    path('skill/add/', views.add_skill, name='add_skill'),
    path('skill/<int:pk>/delete/', views.delete_skill, name='delete_skill'),
    path('project/add/', views.add_project, name='add_project'),
    path('project/<int:pk>/delete/', views.delete_project, name='delete_project'),
    path('certification/add/', views.add_certification, name='add_certification'),
    path('certification/<int:pk>/delete/', views.delete_certification, name='delete_certification'),
    path('custom/add/', views.add_custom_entry, name='add_custom_entry'),
    path('custom/<int:pk>/delete/', views.delete_custom_entry, name='delete_custom_entry'),
]
