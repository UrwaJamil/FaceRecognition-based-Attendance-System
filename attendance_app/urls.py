from django.urls import path
from .views import *


urlpatterns = [
    path('api/members/', MemberCreateView.as_view()),
    path('api/recognize-face/', FaceRecognitionView.as_view()),
    path('api/attendance/today/', TodayAttendanceView.as_view()),
    path('api/attendance/live/', LiveAttendanceView.as_view()),
    path('api/logs/', RecognitionLogListView.as_view()),

    path('live-display/', live_display_page, name='live_display'),
    path('add-member/', add_member_page, name='add_member'),
    path('today-attendance/', today_attendance_page, name='today_attendance'),
    path('logs/', logs_page, name='logs'),
    path('scan-attendance/', scan_attendance_page, name='scan_attendance'),
    path('secure-face/<str:filename>/', serve_protected_face, name='secure_face'),
    path("employees/", employee_list, name="employee_list"),
    path("employees/<int:member_id>/yearly/", yearly_attendance, name="employee_yearly_log"),
]