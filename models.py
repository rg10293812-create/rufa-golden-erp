import os
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from core.models import UserProfile


class Command(BaseCommand):
    help = 'Create or update the executive account for RUFA GOLD ERP.'

    def handle(self, *args, **options):
        username = os.environ.get('DEFAULT_ADMIN_USERNAME', 'ROFA')
        password = os.environ.get('DEFAULT_ADMIN_PASSWORD', 'QQ1122qq11223')
        name = os.environ.get('DEFAULT_ADMIN_NAME', 'ROFA')
        user, created = User.objects.get_or_create(username=username)
        user.first_name = name
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()
        UserProfile.objects.update_or_create(user=user, defaults={'role': UserProfile.EXECUTIVE, 'can_delete_properties': True, 'can_manage_permissions': True})
        self.stdout.write(self.style.SUCCESS(f'Executive account ready: {username}'))
