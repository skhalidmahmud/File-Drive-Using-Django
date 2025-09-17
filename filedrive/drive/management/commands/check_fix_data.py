from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from drive.models import Folder, File

class Command(BaseCommand):
    help = 'Checks and fixes data consistency issues in the file drive'
    
    def handle(self, *args, **options):
        users = User.objects.all()
        
        for user in users:
            self.stdout.write(f"Checking data for user: {user.username}")
            
            # Check root folders
            root_folders = Folder.objects.filter(owner=user, parent=None)
            
            if root_folders.count() == 0:
                self.stdout.write(self.style.WARNING(f"User {user.username} has no root folder. Creating one..."))
                root_folder = Folder.objects.create(name='Home', owner=user, parent=None)
            elif root_folders.count() > 1:
                self.stdout.write(self.style.WARNING(f"User {user.username} has {root_folders.count()} root folders. Cleaning up..."))
                root_folder = root_folders.first()
                
                # Move all files and folders from other root folders to the kept one
                for folder in root_folders[1:]:
                    # Move subfolders
                    for subfolder in folder.children.all():
                        subfolder.parent = root_folder
                        subfolder.save()
                        self.stdout.write(f"Moved folder '{subfolder.name}' to root")
                    
                    # Move files
                    for file in folder.files.all():
                        file.folder = root_folder
                        file.save()
                        self.stdout.write(f"Moved file '{file.name}' to root")
                    
                    # Delete the extra root folder
                    folder.delete()
                    self.stdout.write(f"Deleted extra root folder")
            else:
                root_folder = root_folders.first()
            
            # Check for orphaned files (not in any folder)
            orphaned_files = File.objects.filter(owner=user, folder=None)
            if orphaned_files.exists():
                self.stdout.write(self.style.WARNING(f"Found {orphaned_files.count()} orphaned files for user {user.username}. Moving to root..."))
                for file in orphaned_files:
                    file.folder = root_folder
                    file.save()
                    self.stdout.write(f"Moved orphaned file '{file.name}' to root")
            
            # Check for orphaned folders (not in any folder and not root)
            orphaned_folders = Folder.objects.filter(owner=user, parent=None).exclude(id=root_folder.id)
            if orphaned_folders.exists():
                self.stdout.write(self.style.WARNING(f"Found {orphaned_folders.count()} orphaned folders for user {user.username}. Moving to root..."))
                for folder in orphaned_folders:
                    folder.parent = root_folder
                    folder.save()
                    self.stdout.write(f"Moved orphaned folder '{folder.name}' to root")
            
            # Print final counts
            folder_count = Folder.objects.filter(owner=user).count()
            file_count = File.objects.filter(owner=user).count()
            root_folder_count = Folder.objects.filter(owner=user, parent=None).count()
            
            self.stdout.write(self.style.SUCCESS(f"User {user.username} now has:"))
            self.stdout.write(self.style.SUCCESS(f"- {root_folder_count} root folder(s)"))
            self.stdout.write(self.style.SUCCESS(f"- {folder_count} total folders"))
            self.stdout.write(self.style.SUCCESS(f"- {file_count} total files"))
            self.stdout.write(self.style.SUCCESS(f"- {root_folder.children.count()} subfolders in root"))
            self.stdout.write(self.style.SUCCESS(f"- {root_folder.files.count()} files in root"))
            self.stdout.write("------")