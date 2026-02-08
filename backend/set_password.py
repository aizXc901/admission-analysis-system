#!/usr/bin/env python
import os
import sys
import django
from django.contrib.auth import get_user_model

# Add the project directory to Python path
sys.path.append('/workspace/backend')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admission_api.settings')
django.setup()

# Change the password
User = get_user_model()
admin_user = User.objects.get(username='admin')
admin_user.set_password('admin123')
admin_user.save()

print("Admin password updated successfully!")