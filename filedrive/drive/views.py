from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse, Http404
from django.urls import reverse
from django.core.paginator import Paginator
from django.utils import timezone
from .models import UserProfile, Folder, File, Trash, RecentActivity, StorageSettings
from .forms import UserProfileForm, FolderForm, FileForm
import os
from datetime import datetime

def dp(user):
    User = UserProfile.objects.get(user=user)
    profileIMG = User.photo
    return profileIMG

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            # Create root folder for the user only if it doesn't exist
            if not Folder.objects.filter(owner=user, parent=None).exists():
                Folder.objects.create(name='Home', owner=user, parent=None)
            messages.success(request, "Account created successfully!")
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'drive/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'drive/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def home_view(request):
    user = UserProfile.objects.get(user=request.user)
    # Get user's root folder
    try:
        root_folders = Folder.objects.filter(owner=request.user, parent=None)
        if root_folders.exists():
            if root_folders.count() > 1:
                # If multiple root folders exist, use the first one and log a warning
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"User {request.user.username} has {root_folders.count()} root folders. Using the first one.")
                root_folder = root_folders.first()
            else:
                root_folder = root_folders.first()
        else:
            # If no root folder exists, create one
            root_folder = Folder.objects.create(name='Home', owner=request.user, parent=None)
    except Exception as e:
        # Handle any other exceptions
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error getting root folder for user {request.user.username}: {str(e)}")
        # Create a new root folder as fallback
        root_folder = Folder.objects.create(name='Home', owner=request.user, parent=None)
    
    # Get recent activities
    recent_activities = RecentActivity.objects.filter(user=request.user)[:6]
    
    # Get storage usage
    storage_settings = StorageSettings.objects.first()
    if not storage_settings:
        storage_settings = StorageSettings.objects.create()
    
    used_space = File.objects.filter(owner=request.user).aggregate(total=Sum('size'))['total'] or 0
    total_space = storage_settings.space_per_user
    used_percentage = (used_space / total_space) * 100 if total_space > 0 else 0
    
    # Debug: Print information to console
    print(f"Root folder: {root_folder}")
    print(f"Subfolders count: {root_folder.children.count()}")
    print(f"Files count: {root_folder.files.count()}")
    
    # If there are files/folders not showing in the root folder, 
    # let's also check for files/folders that might be orphaned
    all_user_folders = Folder.objects.filter(owner=request.user)
    all_user_files = File.objects.filter(owner=request.user)
    
    print(f"All user folders: {all_user_folders.count()}")
    print(f"All user files: {all_user_files.count()}")
    
    # Check for orphaned files/folders (not in any folder)
    orphaned_folders = all_user_folders.filter(parent=None).exclude(id=root_folder.id)
    orphaned_files = all_user_files.filter(folder=None)
    
    print(f"Orphaned folders: {orphaned_folders.count()}")
    print(f"Orphaned files: {orphaned_files.count()}")
    
    # If there are orphaned items, move them to the root folder
    for folder in orphaned_folders:
        print(f"Moving orphaned folder '{folder.name}' to root")
        folder.parent = root_folder
        folder.save()
    
    for file in orphaned_files:
        print(f"Moving orphaned file '{file.name}' to root")
        file.folder = root_folder
        file.save()
    
    # Now get the updated counts
    subfolders = root_folder.children.all()
    files = root_folder.files.all()
    
    context = {
        'root_folder': root_folder,
        'subfolders': subfolders,
        'files': files,
        'recent_activities': recent_activities,
        'used_space': used_space,
        'total_space': total_space,
        'used_percentage': used_percentage,
        'img': user.photo,
    }
    return render(request, 'drive/home.html', context)

@login_required
def folder_view(request, folder_id):
    user = UserProfile.objects.get(user=request.user)
    folder = get_object_or_404(Folder, id=folder_id, owner=request.user)
    
    # Check if folder is public or user is owner
    if not folder.is_public and folder.owner != request.user:
        raise Http404("Folder not found or you don't have permission to access it.")
    
    subfolders = folder.children.all()
    files = folder.files.all()
    
    # Record activity if user is not the owner
    if folder.owner != request.user:
        RecentActivity.objects.create(
            user=request.user,
            action="viewed",
            item_name=folder.name,
            item_type="folder"
        )
    
    context = {
        'folder': folder,
        'subfolders': subfolders,
        'files': files,
        'img': user.photo,
    }
    return render(request, 'drive/folder.html', context)

@login_required
def create_folder_view(request, parent_id=None):
    user = UserProfile.objects.get(user=request.user)
    parent_folder = None
    if parent_id:
        parent_folder = get_object_or_404(Folder, id=parent_id, owner=request.user)
    
    if request.method == 'POST':
        form = FolderForm(request.POST)
        if form.is_valid():
            folder = form.save(commit=False)
            folder.owner = request.user
            folder.parent = parent_folder
            folder.save()
            
            # Record activity
            RecentActivity.objects.create(
                user=request.user,
                action="created",
                item_name=folder.name,
                item_type="folder"
            )
            
            messages.success(request, "Folder created successfully!")
            if parent_folder:
                return redirect('folder', folder_id=parent_folder.id)
            return redirect('home')
    else:
        form = FolderForm()
    
    context = {
        'form': form,
        'parent_folder': parent_folder,
        'img': user.photo,
    }
    return render(request, 'drive/create_folder.html', context)

@login_required
def upload_file_view(request, folder_id=None):
    user = UserProfile.objects.get(user=request.user)
    folder = None
    if folder_id:
        folder = get_object_or_404(Folder, id=folder_id, owner=request.user)
    
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            file_obj = form.save(commit=False)
            file_obj.owner = request.user
            file_obj.folder = folder
            
            # Auto-populate name from filename if not provided
            if not file_obj.name and file_obj.file:
                file_obj.name = file_obj.file.name.split('/')[-1]
            
            file_obj.save()
            
            # Check storage space
            storage_settings = StorageSettings.objects.first()
            if not storage_settings:
                storage_settings = StorageSettings.objects.create()
            
            used_space = File.objects.filter(owner=request.user).aggregate(total=Sum('size'))['total'] or 0
            if used_space > storage_settings.space_per_user:
                file_obj.delete()
                messages.error(request, "Not enough storage space!")
                if folder:
                    return redirect('folder', folder_id=folder.id)
                return redirect('home')
            
            # Record activity
            RecentActivity.objects.create(
                user=request.user,
                action="uploaded",
                item_name=file_obj.name,
                item_type="file"
            )
            
            messages.success(request, "File uploaded successfully!")
            if folder:
                return redirect('folder', folder_id=folder.id)
            return redirect('home')
    else:
        form = FileForm()
    
    context = {
        'form': form,
        'folder': folder,
        'img': user.photo,
    }
    return render(request, 'drive/upload_file.html', context)

@login_required
def file_view(request, file_id):
    user = UserProfile.objects.get(user=request.user)
    file_obj = get_object_or_404(File, id=file_id)
    
    # Check if file is public or user is owner
    if not file_obj.is_public and file_obj.owner != request.user:
        raise Http404("File not found or you don't have permission to access it.")
    
    # Record activity if user is not the owner
    if file_obj.owner != request.user:
        RecentActivity.objects.create(
            user=request.user,
            action="viewed",
            item_name=file_obj.name,
            item_type="file"
        )
    
    # Get file extension to determine how to display it
    extension = file_obj.get_extension()
    context = {
        'file': file_obj,
        'extension': extension,
        'img': user.photo,
    }
    return render(request, 'drive/file.html', context)

@login_required
def download_file_view(request, file_id):
    file_obj = get_object_or_404(File, id=file_id)
    
    # Check if file is public or user is owner
    if not file_obj.is_public and file_obj.owner != request.user:
        raise Http404("File not found or you don't have permission to access it.")
    
    # Record activity
    RecentActivity.objects.create(
        user=request.user,
        action="downloaded",
        item_name=file_obj.name,
        item_type="file"
    )
    
    file_path = file_obj.file.path
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/octet-stream")
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
            return response
    raise Http404("File not found")

@login_required
def delete_item_view(request, item_type, item_id):
    if item_type == 'file':
        item = get_object_or_404(File, id=item_id, owner=request.user)
        Trash.objects.create(owner=request.user, file=item)
        # Record activity
        RecentActivity.objects.create(
            user=request.user,
            action="deleted",
            item_name=item.name,
            item_type="file"
        )
        messages.success(request, f"File '{item.name}' moved to trash.")
    elif item_type == 'folder':
        item = get_object_or_404(Folder, id=item_id, owner=request.user)
        Trash.objects.create(owner=request.user, folder=item)
        # Record activity
        RecentActivity.objects.create(
            user=request.user,
            action="deleted",
            item_name=item.name,
            item_type="folder"
        )
        messages.success(request, f"Folder '{item.name}' moved to trash.")
    
    # Redirect to the parent folder or home if it's a root folder
    if item_type == 'file' and item.folder:
        return redirect('folder', folder_id=item.folder.id)
    elif item_type == 'folder' and item.parent:
        return redirect('folder', folder_id=item.parent.id)
    return redirect('home')

@login_required
def trash_view(request):
    trash_items = Trash.objects.filter(owner=request.user)
    user = UserProfile.objects.get(user=request.user)
    context = {
        'trash_items': trash_items,
        'img': user.photo,
    }
    return render(request, 'drive/trash.html', context)

@login_required
def restore_from_trash_view(request, trash_id):
    trash_item = get_object_or_404(Trash, id=trash_id, owner=request.user)
    
    if trash_item.file:
        # Record activity
        RecentActivity.objects.create(
            user=request.user,
            action="restored",
            item_name=trash_item.file.name,
            item_type="file"
        )
        trash_item.delete()
        messages.success(request, f"File '{trash_item.file.name}' restored from trash.")
    elif trash_item.folder:
        # Record activity
        RecentActivity.objects.create(
            user=request.user,
            action="restored",
            item_name=trash_item.folder.name,
            item_type="folder"
        )
        trash_item.delete()
        messages.success(request, f"Folder '{trash_item.folder.name}' restored from trash.")
    
    return redirect('trash')

@login_required
def delete_from_trash_view(request, trash_id):
    trash_item = get_object_or_404(Trash, id=trash_id, owner=request.user)
    
    if trash_item.file:
        file_path = trash_item.file.file.path
        if os.path.exists(file_path):
            os.remove(file_path)
        trash_item.file.delete()
        messages.success(request, f"File '{trash_item.file.name}' permanently deleted.")
    elif trash_item.folder:
        # Delete folder and all its contents
        def delete_folder(folder):
            for subfolder in folder.children.all():
                delete_folder(subfolder)
            for file in folder.files.all():
                file_path = file.file.path
                if os.path.exists(file_path):
                    os.remove(file_path)
                file.delete()
            folder.delete()
        
        delete_folder(trash_item.folder)
        messages.success(request, f"Folder '{trash_item.folder.name}' permanently deleted.")
    
    trash_item.delete()
    return redirect('trash')

@login_required
def toggle_public_view(request, item_type, item_id):
    if item_type == 'file':
        item = get_object_or_404(File, id=item_id, owner=request.user)
        item.is_public = not item.is_public
        item.save()
        status = "public" if item.is_public else "private"
        messages.success(request, f"File '{item.name}' is now {status}.")
    elif item_type == 'folder':
        item = get_object_or_404(Folder, id=item_id, owner=request.user)
        item.is_public = not item.is_public
        item.save()
        status = "public" if item.is_public else "private"
        messages.success(request, f"Folder '{item.name}' is now {status}.")
    
    # Redirect back to the folder or home
    if item_type == 'file' and item.folder:
        return redirect('folder', folder_id=item.folder.id)
    elif item_type == 'folder' and item.parent:
        return redirect('folder', folder_id=item.parent.id)
    return redirect('home')

@login_required
def profile_view(request):
    user = UserProfile.objects.get(user=request.user)
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    
    context = {
        'form': form,
        'img': user.photo,
    }
    return render(request, 'drive/profile.html', context)

@login_required
def search_view(request):
    user = UserProfile.objects.get(user=request.user)
    query = request.GET.get('q', '')
    
    folders = []
    files = []
    
    if query:
        folders = Folder.objects.filter(
            owner=request.user,
            name__icontains=query
        )
        
        files = File.objects.filter(
            owner=request.user,
            name__icontains=query
        )
    
    context = {
        'query': query,
        'folders': folders,
        'files': files,
        'img': user.photo,
    }
    return render(request, 'drive/search.html', context)