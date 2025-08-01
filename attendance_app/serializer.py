from .models import *
from rest_framework import serializers
import base64

class MemberSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = ['id', 'name', 'email', 'image', 'image_url', 'created_at']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            return request.build_absolute_uri(obj.image.url)
        return None
    
class AttendanceSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source = 'member.name', read_only=True)

    class Meta:
        model = Attendance
        fields = ['id', 'member', 'member_name', 'date', 'time']

class CamerDeviceserializer(serializers.ModelSerializer):
    class Meta:
        model = CameraDevice
        fields = ['id', 'name', 'ip_stream_link', 'location', 'is_active']

class RecognitionLogSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source = 'member.name', read_only = True)
    camera_name = serializers.CharField(source = 'camera.name', read_only = True)

    class Meta:
        model = RecognitionLog
        fields = ['id', 'member', 'member_name', 'detected_at', 'recognized', 'camera', 'camera_name', 'confidence']

class FaceRecognitionInputSerializer(serializers.Serializer):
    image = serializers.ImageField()

    def validate_image(self, value):
        return value