from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from drive.models import Folder

class Command(BaseCommand):
    help = 'Cleans up multiple root folders for users, ensuring each user has only one root folder'
    
    def handle(self, *args, **options):
        users = User.objects.all()
        
        for user in users:
            root_folders = Folder.objects.filter(owner=user, parent=None)
            
            if root_folders.count() > 1:
                self.stdout.write(f"User {user.username} has {root_folders.count()} root folders. Cleaning up...")
                
                # Keep the first root folder
                root_folder_to_keep = root_folders.first()
                
                # Move all files and folders from other root folders to the kept one
                for folder in root_folders[1:]:
                    # Move subfolders
                    for subfolder in folder.children.all():
                        subfolder.parent = root_folder_to_keep
                        subfolder.save()
                    
                    # Move files
                    for file in folder.files.all():
                        file.folder = root_folder_to_keep
                        file.save()
                    
                    # Delete the extra root folder
                    folder.delete()
                
                self.stdout.write(self.style.SUCCESS(f"Cleaned up root folders for user {user.username}"))