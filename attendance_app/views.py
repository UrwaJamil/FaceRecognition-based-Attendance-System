from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializer import *
from .models import *
from django.utils.timezone import now
import face_recognition, cv2, pickle, datetime
from django.shortcuts import render


class MemberCreateView(APIView):
    def get(self, request):
        member = Member.objects.all()
        serilaizer = MemberSerializer(member, many=True, context={'request': request})
        return Response(serilaizer.data)
    
    def post(self, request):
        serializer = MemberSerializer(data = request.data, context={'request': request})
        if serializer.is_valid():
            member = serializer.save()

            image_path = member.image.path
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)

            if encodings:
              member.encoding = pickle.dumps(encodings[0])
              member.save()
            else:
              member.delete()
              return Response({"error": "No face found in image"}, status=400) 
        return Response(serializer.errors, status=400)
    
class FaceRecognitionView(APIView):
   def post(self, request):
      serilaizer = FaceRecognitionInputSerializer(data = request.data)
      if not serilaizer.is_valid():
         return Response(serilaizer.errors, status=400)
      
      image = face_recognition.load_image_file(serilaizer.validate_image['image'])
      encodings = face_recognition.face_encodings(image)
      if not encodings:
         return Response({"detail": "No face detected"}, status=400)
      
      input_encoding = encodings[0]
      known_numbers = Member.objects.exclude(encodings=None)
      
      for member in known_numbers:
        known_encoding = pickle.loads(member.encoding)
        match = face_recognition.compare_faces([known_encoding], input_encoding)[0]

        if match:
           today = datetime.date.today()
           attendance , created = Attendance.objects.get_or_create(member=member, date=today)

           RecognitionLog.objects.create(member=member, recognized=True, confidence=1.0)
           return Response({
              "status": "Recognized",
              "name": member.name,
              "attendance": "marked" if created else "already_marked"
           })
        
      RecognitionLog.objects.create(member=None, recognized=False, confidence=0.0)
      return Response({"status": "Not Recognized"}, status=404)
   
class TodayAttendanceView(APIView):
   def get(self, request):
      today = datetime.date.today()
      attendance = Attendance.objects.filter(date=today)
      serializer = AttendanceSerializer(attendance, many=True)
      return Response(serializer.data)
   
class LiveAttendanceView(APIView):
   def get(self, request):
      attendance = Attendance.objects.order_by('-id')[:5]
      serializer = AttendanceSerializer(attendance, many=True)
      return Response(serializer.data)
   
class RecognitionLogListView(APIView):
   def get(self, request):
      log = RecognitionLog.objects.order_by('-detected_at')[:10]
      serializer = RecognitionLogSerializer(log, many=True)
      return Response(serializer.data)
   

def live_display_page(request):
    return render(request, 'attendance_app/live_display.html')

def add_member_page(request):
    return render(request, 'attendance_app/add_member.html')

def today_attendance_page(request):
    return render(request, 'attendance_app/today_attendance.html')

def logs_page(request):
    return render(request, 'attendance_app/logs.html')

def scan_attendance_page(request):
    return render(request, 'attendance_app/scan_attendance.html')