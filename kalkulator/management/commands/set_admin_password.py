"""
Management command: admin jelszó beállítása környezeti változóból.
A Railway-en az ADMIN_PASSWORD változóban tároljuk a jelszót.
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Beállítja az admin felhasználó jelszavát az ADMIN_PASSWORD környezeti változóból'

    def handle(self, *args, **options):
        password = os.environ.get('ADMIN_PASSWORD', '')
        if not password:
            self.stdout.write(self.style.WARNING(
                'ADMIN_PASSWORD változó nincs beállítva → jelszócsere kihagyva.'
            ))
            return

        try:
            user = User.objects.get(username='admin')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                'HIBA: admin felhasználó nem található!'
            ))
            return

        user.set_password(password)
        user.save()
        self.stdout.write(self.style.SUCCESS(
            f'Admin jelszó sikeresen beállítva.'
        ))
