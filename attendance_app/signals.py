from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Member
import subprocess
import os

@receiver(post_save, sender=Member)
def build_face_encoding(sender, instance, created, **kwargs):
    if created:
        script_path = os.path.join(os.path.dirname(__file__), '../face_utils/build_known_faces.py')
        subprocess.call(['python', script_path])
