
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



### Install pytesseract
pytesseract is a Python wrapper for Google's Tesseract-OCR Engine. To use OCR functionalities, you need to install both pytesseract and Tesseract-OCR. Follow these steps:

Install Tesseract-OCR:

On Ubuntu:
```bash
sudo apt-get install tesseract-ocr
```


On macOS (using Homebrew):

```bash
brew install tesseract
```



On Windows:

Download the installer from the Tesseract at UB Mannheim and follow the installation instructions.

Install the pytesseract Python package:

```bash
pip install pytesseract
```



Configure pytesseract to use the Tesseract executable:

You may need to set the TESSDATA_PREFIX environment variable or configure pytesseract to point to the Tesseract executable if it is not in your PATH.
```
python
import pytesseract
```

# On Windows, you might need to specify the path to tesseract.exe
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

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
