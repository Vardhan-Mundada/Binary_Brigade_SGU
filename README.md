
# FinSo

FinSo is a comprehensive personal finance management application offering features like transaction management, investment tracking, financial reporting, and more. The application also provides SMS automation, spam detection, and various other financial utilities.

## Installation and Setup

### Clone the Repository

```bash
git clone https://github.com/Vardhan-Mundada/Binary_Brigade_SGU.git
cd finsoproject
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Setup and Configuration

#### Database Configuration

1. Create a MySQL database:

    ```bash
    mysql -u root -p
    CREATE DATABASE finsodb;
    ```

2. Update the `settings.py` file with your database credentials:

    ```python
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'finsodb',
            'USER': 'yourusername',
            'PASSWORD': 'yourpassword',
            'HOST': 'localhost',
            'PORT': '3306',
        }
    }
    ```

#### Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

### Installing the APK on Android

1. Navigate to the `apk` directory in the project root.
2. Transfer the APK file to your Android device.
3. Open the APK file on your device to install the FinSo app.
4. Follow the on-screen instructions to complete the installation.

---
