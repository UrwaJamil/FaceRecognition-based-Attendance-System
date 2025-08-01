from django.db import models

class Member(models.Model):
    name = models.CharField(max_length=50),
    email = models.EmailField(unique=True),
    image = models.ImageField(upload_to = 'faces/'),
    encoding = models.BinaryField(null=True, blank=True),
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Attendance(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)

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