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
    
    def save(self, *args, **kwargs):
        if not self.size:
            self.size = self.file.size
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