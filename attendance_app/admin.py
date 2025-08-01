from django.contrib import admin
from .models import *

admin.site.register(Member),
admin.site.register(Attendance),
admin.site.register(CameraDevice), 
admin.site.register(RecognitionLog)