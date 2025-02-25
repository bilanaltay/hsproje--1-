from django.urls import path
from . import views

urlpatterns = [
    path('user_list/', views.user_list, name='user_list'),  # Kullanıcıları listeleyen URL
    path('create_user/', views.create_user, name='create_user'),  # Kullanıcı eklemek için URL
    path('create_project/', views.create_project, name='create_project'),
    path('login/', views.login, name='login_user'),

    # Tüm projeleri ve kullanıcıları listeleme işlemi
    path('projects/', views.list_projects, name='list_projects'),
    path('project/<int:project_id>/', views.get_project_details, name='get_project_details'),  # Projeyi detaylı görmek


    path('add_user_to_project/<int:project_id>/', views.add_user_to_project, name='add_user_to_project'),

    path('tasks/create/', views.create_task, name='create_task'),
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/<int:task_id>/', views.task_detail, name='task_detail'),
] 