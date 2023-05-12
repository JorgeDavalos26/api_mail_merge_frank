from django.urls import path
from .views import get_users, create_user, get_user, delete_user, update_user, create_and_download_texts, create_and_download_pdfs, get_template, update_template

urlpatterns = [
    path('users/', get_users, name='user_list'),
    path('users/<int:user_id>/', get_user, name='user_detail'),
    path('users/create/', create_user, name='user_create'),
    path('users/<int:user_id>/update/', update_user, name='user_update'),
    path('users/<int:user_id>/delete/', delete_user, name='user_delete'),
    path('texts/download/', create_and_download_texts, name='create_and_download_texts'),
    path('pdfs/download/', create_and_download_pdfs, name='create_and_download_pdfs'),
    path('template/', get_template, name='get_template'),
    path('template/update', update_template, name='update_template'),
]

