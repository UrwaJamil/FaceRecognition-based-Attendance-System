from django.db import models
import uuid
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage

def protected_face_upload_path(instance, filename):
    # Unique and non-identifiable filename
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('faces',filename)

class Member(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)

    # Secure face image storage
    face_file = models.FileField(
        upload_to='', 
        storage=FileSystemStorage(location=os.path.join(settings.BASE_DIR, 'secure_faces')),
        null= True, blank= True
    )

    # Pickled face encoding (128-d vector)
    encoding = models.BinaryField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# class Member(models.Model):
#     name = models.CharField(max_length=50)
#     email = models.EmailField(unique=True)
#     image = models.ImageField(upload_to = 'faces/')
#     encoding = models.BinaryField(null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.name
    
class Attendance(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('member','date')

    def __str__(self):
        return f"{self.member.name}-{self.date}"
    
class CameraDevice(models.Model):
    name = models.CharField()
    ip_stream_link = models.URLField()
    location = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
class RecognitionLog(models.Model):
    member =models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True)
    detected_at = models.DateTimeField(auto_now_add=True)
    recognized = models.BooleanField(default=False)
    camera = models.ForeignKey(CameraDevice, on_delete=models.SET_NULL, null=True, blank=True)
    confidence = models.FloatField(null=True , blank=True)

    def __str__(self):
        return f"{self.member} - {'Success' if self.recognized else 'Failed'}"