from django.contrib import admin
from .models import UserProfile, Folder, File, Trash, RecentActivity, StorageSettings

@admin.register(StorageSettings)
class StorageSettingsAdmin(admin.ModelAdmin):
    list_display = ['id', 'space_per_user_gb']
    
    def space_per_user_gb(self, obj):
        return f"{obj.space_per_user / (1024*1024*1024):.2f} GB"
    space_per_user_gb.short_description = "Space per user"

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'gender', 'date_of_birth']
    list_filter = ['gender']
    search_fields = ['user__username']

@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'parent', 'created_at', 'is_public']
    list_filter = ['is_public', 'created_at']
    search_fields = ['name', 'owner__username']

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'folder', 'size', 'file_type', 'created_at', 'is_public']
    list_filter = ['file_type', 'is_public', 'created_at']
    search_fields = ['name', 'owner__username']

@admin.register(Trash)
class TrashAdmin(admin.ModelAdmin):
    list_display = ['owner', 'item_name', 'item_type', 'deleted_at']
    list_filter = ['deleted_at']
    search_fields = ['owner__username']
    
    def item_name(self, obj):
        if obj.file:
            return obj.file.name
        return obj.folder.name
    
    def item_type(self, obj):
        if obj.file:
            return "File"
        return "Folder"

@admin.register(RecentActivity)
class RecentActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'item_name', 'item_type', 'timestamp']
    list_filter = ['action', 'item_type', 'timestamp']
    search_fields = ['user__username', 'item_name']