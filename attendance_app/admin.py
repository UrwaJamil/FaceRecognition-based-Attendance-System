from django.contrib import admin
from .models import *

admin.site.register(Attendance),
admin.site.register(CameraDevice), 
admin.site.register(RecognitionLog)

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        # Only superusers can view objects
        if request.user.is_superuser:
            return super().get_queryset(request)
        return super().get_queryset(request).none()

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return False  # or True, depending on your logic

    # Hide the image field in the admin
    exclude = ('image',)