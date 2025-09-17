from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Main views
    path('', views.home_view, name='home'),
    path('folder/<int:folder_id>/', views.folder_view, name='folder'),
    path('file/<int:file_id>/', views.file_view, name='file'),
    path('download/<int:file_id>/', views.download_file_view, name='download_file'),
    
    # Create views
    path('create-folder/', views.create_folder_view, name='create_folder'),
    path('create-folder/<int:parent_id>/', views.create_folder_view, name='create_folder_in_parent'),
    path('upload-file/', views.upload_file_view, name='upload_file'),
    path('upload-file/<int:folder_id>/', views.upload_file_view, name='upload_file_to_folder'),
    
    # Delete/Trash views
    path('delete/<str:item_type>/<int:item_id>/', views.delete_item_view, name='delete_item'),
    path('trash/', views.trash_view, name='trash'),
    path('restore/<int:trash_id>/', views.restore_from_trash_view, name='restore_from_trash'),
    path('delete-permanent/<int:trash_id>/', views.delete_from_trash_view, name='delete_from_trash'),
    
    # Other views
    path('toggle-public/<str:item_type>/<int:item_id>/', views.toggle_public_view, name='toggle_public'),
    path('profile/', views.profile_view, name='profile'),
    path('search/', views.search_view, name='search'),
]