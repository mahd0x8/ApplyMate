from django.urls import path
from . import views

urlpatterns = [
    path('', views.application_list, name='application_list'),
    path('new/', views.application_create, name='application_create'),
    path('<int:pk>/', views.application_detail, name='application_detail'),
    path('<int:pk>/update/', views.application_update, name='application_update'),
    path('<int:pk>/move/', views.application_move, name='application_move'),
    path('<int:pk>/delete/', views.application_delete, name='application_delete'),
    path('<int:pk>/chat/', views.chat_message, name='chat_message'),
    path('<int:pk>/generate/', views.generate_document, name='generate_document'),
    path('doc/<int:doc_id>/export/<str:fmt>/', views.export_document, name='export_document'),
]
