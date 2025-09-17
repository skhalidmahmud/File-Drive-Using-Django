# FileDrive - A Cloud Storage Solution

FileDrive is a Django-based cloud storage application similar to Google Drive, allowing users to store, manage, and share files online. Users can create folders, upload files, organize their content, and control sharing permissions.

## Features

- **User Authentication**: Secure login/signup system for user access
- **File Management**: Upload, organize, download, and delete files
- **Folder Organization**: Create nested folder structures for better organization
- **Storage Management**: Configurable storage limits per user (default: 1GB)
- **File Preview**: Built-in viewers for images, videos, audio, PDFs, and text files
- **Sharing Options**: Public or private sharing for files and folders
- **Trash System**: Recover deleted items or permanently remove them
- **Recent Activity**: Track recent file and folder actions
- **Search Functionality**: Find files and folders quickly
- **User Profiles**: Manage personal information and profile photos
- **Drag & Drop**: Easy file uploading with drag-and-drop support
- **Progress Tracking**: Visual representation of storage usage

## Technology Stack

- **Backend**: Django 4.x
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Database**: SQLite (development), can be configured for PostgreSQL/MySQL (production)
- **File Storage**: Django's file system storage
- **Icons**: Bootstrap Icons

## Live Demo

Check out the live demo at [https://drive.thinkori.com/](https://drive.thinkori.com/)

## Installation

### Prerequisites

- Python 3.8+
- pip
- virtualenv (recommended)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/skhalidmahmud/filedrive.git
   cd filedrive
   ```

2. Create and activate a virtual environment:
   ```bash
   virtualenv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Apply migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

7. Access the application at `http://localhost:8000`

## Configuration

### Storage Settings

To configure the default storage space per user:

1. Go to the Django admin panel at `http://localhost:8000/admin`
2. Navigate to "Drive" > "Storage Settings"
3. Update the "Space per user" field (in bytes)
   - 1 GB = 1073741824 bytes
   - 5 GB = 5368709120 bytes

### Media Files

For production, configure your web server to serve media files:

```python
# settings.py
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

## Usage

### For Users

1. **Sign Up**: Create a new account with a username and password
2. **Login**: Access your account with your credentials
3. **Upload Files**: Click "Upload File" or drag and drop files
4. **Create Folders**: Organize your files with folders
5. **Share Files**: Toggle public/private sharing for files and folders
6. **View Files**: Preview images, videos, audio, PDFs, and text files
7. **Download Files**: Save files to your device
8. **Manage Storage**: Monitor your storage usage in the sidebar
9. **Search**: Find files and folders using the search bar
10. **Profile**: Update your profile information and photo

### For Administrators

1. **User Management**: Manage user accounts through the Django admin
2. **Storage Configuration**: Adjust storage limits per user
3. **Content Monitoring**: View and manage user files and folders
4. **Activity Tracking**: Monitor user activity through the RecentActivity model

## Project Structure

```
filedrive/
├── drive/                 # Main application
│   ├── migrations/        # Database migrations
│   ├── templates/        # HTML templates
│   │   └── drive/        # App-specific templates
│   ├── templatetags/     # Custom template filters
│   ├── __init__.py
│   ├── admin.py          # Django admin configuration
│   ├── apps.py           # App configuration
│   ├── forms.py          # Form classes
│   ├── models.py         # Database models
│   ├── tests.py          # Test cases
│   ├── urls.py           # URL patterns
│   └── views.py          # View functions
├── filedive/             # Project settings
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py       # Django settings
│   ├── urls.py           # Root URL configuration
│   └── wsgi.py
├── media/                # User-uploaded files
├── requirements.txt      # Python dependencies
└── manage.py            # Django management script
```

## API Reference

### Models

#### User
- Standard Django User model
- Extended with UserProfile for additional information

#### StorageSettings
- `space_per_user`: Storage limit per user in bytes

#### UserProfile
- `user`: One-to-one relationship with User
- `photo`: Profile picture
- `gender`: User's gender
- `date_of_birth`: User's date of birth

#### Folder
- `name`: Folder name
- `owner`: User who owns the folder
- `parent`: Parent folder (for nested structure)
- `created_at`: Creation timestamp
- `modified_at`: Last modification timestamp
- `is_public`: Public visibility flag

#### File
- `name`: File name
- `owner`: User who owns the file
- `folder`: Parent folder
- `file`: File path
- `size`: File size in bytes
- `created_at`: Creation timestamp
- `modified_at`: Last modification timestamp
- `is_public`: Public visibility flag
- `file_type`: File extension/type

#### Trash
- `owner`: User who owns the item
- `file`: Reference to deleted file
- `folder`: Reference to deleted folder
- `deleted_at`: Deletion timestamp

#### RecentActivity
- `user`: User who performed the action
- `action`: Action performed (e.g., "uploaded", "viewed")
- `item_name`: Name of the item
- `item_type`: Type of item ("file" or "folder")
- `timestamp`: Action timestamp

### Views

#### Authentication
- `signup_view`: User registration
- `login_view`: User login
- `logout_view`: User logout

#### Main Views
- `home_view`: User dashboard
- `folder_view`: Display folder contents
- `file_view`: Display file details and preview
- `download_file_view`: Download a file

#### Management Views
- `create_folder_view`: Create a new folder
- `upload_file_view`: Upload a new file
- `delete_item_view`: Move item to trash
- `trash_view`: Display trash contents
- `restore_from_trash_view`: Restore item from trash
- `delete_from_trash_view`: Permanently delete item

#### Other Views
- `toggle_public_view`: Toggle public/private sharing
- `profile_view`: User profile management
- `search_view`: Search for files and folders

## Author

**Khalid Mahmud**

- GitHub: [https://github.com/skhalidmahmud/](https://github.com/skhalidmahmud/)
- LinkedIn: [https://www.linkedin.com/in/skhalidmahmud/](https://www.linkedin.com/in/skhalidmahmud/)
- Portfolio: [http://khalid.top/](http://khalid.top/)

## Working Organization

**Thinkori**

- Website: [https://thinkori.com/](https://thinkori.com/)
- GitHub: [https://github.com/thinkori](https://github.com/thinkori)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter any issues or have questions, please open an issue on the GitHub repository.

## Roadmap

- [ ] Mobile app development
- [ ] File versioning
- [ ] Collaborative editing
- [ ] Advanced sharing permissions
- [ ] File commenting
- [ ] Third-party integrations (Google Drive, Dropbox)
- [ ] End-to-end encryption
- [ ] Bulk operations
- [ ] Keyboard shortcuts
- [ ] Dark mode
- [ ] Multi-language support