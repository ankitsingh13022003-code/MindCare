from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('quiz/', views.quiz_view, name='quiz'),
    path('result/<int:assessment_id>/', views.result_view, name='result'),
    path('guidance/', views.guidance_view, name='guidance'),
    path('contact/', views.contact_view, name='contact'),
    # Admin URLs
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/questions/', views.admin_questions, name='admin_questions'),
    path('admin-panel/questions/add/', views.admin_add_question, name='admin_add_question'),
    path('admin-panel/questions/<int:question_id>/edit/', views.admin_edit_question, name='admin_edit_question'),
    path('admin-panel/questions/<int:question_id>/delete/', views.admin_delete_question, name='admin_delete_question'),
    path('admin-panel/messages/', views.admin_contact_messages, name='admin_contact_messages'),
    path('admin-panel/messages/<int:message_id>/', views.admin_view_message, name='admin_view_message'),
    path('admin-panel/messages/<int:message_id>/delete/', views.admin_delete_message, name='admin_delete_message'),
]



