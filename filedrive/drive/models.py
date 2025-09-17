from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os

class StorageSettings(models.Model):
    space_per_user = models.BigIntegerField(default=1024*1024*1024)  # 1GB in bytes
    
    class Meta:
        verbose_name = "Storage Setting"
        verbose_name_plural = "Storage Settings"
    
    def __str__(self):
        return f"{self.space_per_user / (1024*1024*1024):.2f} GB per user"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return self.user.username

class Folder(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='children')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Folder"
        verbose_name_plural = "Folders"
    
    def __str__(self):
        return self.name
    
    def get_path(self):
        path = []
        current = self
        while current:
            path.append(current.name)
            current = current.parent
        return '/'.join(reversed(path))

class File(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, blank=True, null=True, related_name='files')
    file = models.FileField(upload_to='user_files/')
    size = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=False)
    file_type = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        verbose_name = "File"
        verbose_name_plural = "Files"
    
    def __str__(self):
        return self.name
    
    def get_extension(self):
        return os.path.splitext(self.name)[1][1:].lower()
    
    def get_file_category(self):
        """Return the category of the file based on its extension"""
        extension = self.get_extension()
        
        # Images
        if extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp']:
            return 'image'
        
        # Videos
        elif extension in ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv']:
            return 'video'
        
        # Audio
        elif extension in ['mp3', 'wav', 'flac', 'aac', 'ogg', 'wma']:
            return 'audio'
        
        # Documents
        elif extension in ['pdf']:
            return 'pdf'
        elif extension in ['doc', 'docx']:
            return 'word'
        elif extension in ['xls', 'xlsx']:
            return 'excel'
        elif extension in ['ppt', 'pptx']:
            return 'powerpoint'
        
        # Text
        elif extension in ['txt', 'md', 'py', 'js', 'html', 'css', 'scss', 'json', 'xml', 'csv']:
            return 'text'
        
        # Archives
        elif extension in ['zip', 'rar', 'tar', 'gz', '7z']:
            return 'archive'
        
        # Default
        else:
            return 'other'
    
    def save(self, *args, **kwargs):
        # Auto-populate name from filename if not provided
        if not self.name and self.file:
            self.name = self.file.name.split('/')[-1]
        
        # Set file size
        if not self.size and self.file:
            self.size = self.file.size
        
        # Set file type based on extension
        if not self.file_type:
            self.file_type = self.get_extension()
        
        super().save(*args, **kwargs)

class Trash(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.ForeignKey(File, on_delete=models.CASCADE, blank=True, null=True)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, blank=True, null=True)
    deleted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Trash Item"
        verbose_name_plural = "Trash Items"
    
    def __str__(self):
        if self.file:
            return f"File: {self.file.name}"
        return f"Folder: {self.folder.name}"

class RecentActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)  # e.g., "uploaded", "viewed", "deleted"
    item_name = models.CharField(max_length=255)
    item_type = models.CharField(max_length=10)  # "file" or "folder"
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Recent Activity"
        verbose_name_plural = "Recent Activities"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} {self.action} {self.item_name}"