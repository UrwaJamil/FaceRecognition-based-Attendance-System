from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializer import *
from .models import *
from django.utils.timezone import now
import face_recognition, cv2, pickle, datetime
from django.shortcuts import render
from face_utils.encoding import get_face_encoding
from face_utils.matcher import match_face
from face_utils.attendance import mark_attendance
import os
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.http import FileResponse, Http404
from django.conf import settings
import os
from face_utils.build_known_faces import build_known_faces
import datetime
from django.utils import timezone


class MemberCreateView(APIView):
    def get(self, request):
        member = Member.objects.all()
        serilaizer = MemberSerializer(member, many=True, context={'request': request})
        return Response(serilaizer.data)
    
    def post(self, request):
        serializer = MemberSerializer(data = request.data, context={'request': request})
        if not serializer.is_valid():
            return Response({"error": "❌ Invalid data", "details": serializer.errors}, status=400)
        
        member = serializer.save()
            
        image_path = member.face_file.path
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)

        if not encodings:
            member.delete()
            return Response(
                {"error": "❌ No face found in the image. Please upload a clearer photo."},
                status=400
            )
        new_encoding = encodings[0]
        for existing in Member.objects.exclude(encoding=None):
            existing_encoding = pickle.loads(existing.encoding)
            match = face_recognition.compare_faces(
                [existing_encoding], new_encoding, tolerance=0.6
            )[0]
            if match:
                member.delete()
                return Response(
                    {"error": "❌ This face already exists in the system."},
                    status=400
                )
        member.encoding = pickle.dumps(new_encoding)
        member.save()
        build_known_faces()
        return Response({"detail": "Member added successfully."}, status=201)

class FaceRecognitionView(APIView):
    def post(self, request):
        serializer = FaceRecognitionInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Invalid input", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        temp_path = "temp.jpg"
        try:
            # Save uploaded image
            with open(temp_path, "wb+") as f:
                for chunk in serializer.validated_data["image"].chunks():
                    f.write(chunk)

            # Detect multiple encodings
            unknown_encodings = get_face_encoding(temp_path)  # 👈 ye ab list return karega
            if not unknown_encodings or len(unknown_encodings) == 0:
                RecognitionLog.objects.create(
                    recognized=False,
                    confidence=0.0,
                    error="No face detected"
                )
                return Response(
                    {"detail": "No face detected in image"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Load known encodings from pickle
            try:
                with open("known_faces.pkl", "rb") as f:
                    known_data = pickle.load(f)
                    known_encodings = known_data["encodings"]
                    member_ids = known_data["members"]
            except Exception as e:
                return Response(
                    {"error": "System configuration error", "details": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            results = []
            unknown_count = 0

            # Loop through each detected face
            for unknown_encoding in unknown_encodings:
                match_index, confidence = match_face(
                    unknown_encoding,
                    known_encodings,
                    tolerance=0.40
                )

                if match_index is not None and confidence > 0.5:
                    try:
                        member = Member.objects.get(id=member_ids[match_index])
                        mark_attendance(member, confidence=confidence)

                        results.append({
                            "status": "recognized",
                            "member_id": member.id,
                            "name": member.name,
                            "confidence": round(confidence, 2)
                        })
                    except Member.DoesNotExist:
                        unknown_count += 1
                        RecognitionLog.objects.create(
                            recognized=False,
                            confidence=0.0,
                            error="Matched ID not found in DB"
                        )
                    
                else:
                    unknown_count += 1
                    results.append({
                        "status": "unknown",
                        "confidence": 0.0
                    })

            return Response({
                "recognized": results,
                "unknown_count": unknown_count
            })

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


class TodayAttendanceView(APIView):
   def get(self, request):
      today = timezone.localdate()
      attendance = Attendance.objects.filter(date=today)
      serializer = AttendanceSerializer(attendance, many=True)
      return Response(serializer.data)
   
class LiveAttendanceView(APIView):
   def get(self, request):
      today = timezone.localdate()
      attendance = Attendance.objects.filter(date=today).order_by('-check_in')[:5]
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
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        image = request.FILES.get('face_file')

        if name and email and image:
            # Process image for face encoding
            img = face_recognition.load_image_file(image)
            encodings = face_recognition.face_encodings(img)

            if encodings:
                encoding = encodings[0]
                # Save member
                member = Member(
                    name=name,
                    email=email,
                    face_file=image,
                    encoding=pickle.dumps(encoding)
                )
                member.save()
                return HttpResponse("1")  # ✅ success
            else:
                return HttpResponse("no_face")  # ❌ face not found
        else:
            return HttpResponse("missing_field")  # ❌ any field missing

    return render(request, 'attendance_app/add_member.html')

def today_attendance_page(request):
    return render(request, 'attendance_app/today_attendance.html')

def logs_page(request):
    return render(request, 'attendance_app/logs.html')

@csrf_exempt
def scan_attendance_page(request):
    return render(request, 'attendance_app/scan_attendance.html')

@staff_member_required
def serve_protected_face(request, filename):
    secure_dir = os.path.join(settings.BASE_DIR, 'secure_faces')  # same as FileSystemStorage location
    file_path = os.path.join(secure_dir, filename)

    if not os.path.exists(file_path):
        raise Http404("File not found")

    return FileResponse(open(file_path, 'rb'), content_type='image/jpeg')

from datetime import datetime, time, timedelta
from django.utils.timezone import localtime

def employee_list(request):
    today = datetime.today().date()
    employees = Member.objects.all()
    data = []

    checkin_time = time(11, 0)   # 12:00 PM
    checkout_time = time(16, 0)  # 04:00 PM
    grace = timedelta(minutes=30)

    for emp in employees:
        record = Attendance.objects.filter(member=emp, date=today).first()

        status = "absent"
        today_check_in = None
        today_check_out = None

        if record:
            if record.check_in:
                today_check_in = localtime(record.check_in).strftime("%H:%M")
                in_time = record.check_in.time()
                if in_time < (datetime.combine(today, checkin_time) - grace).time():
                    status = "early_in"
                elif abs(datetime.combine(today, in_time) - datetime.combine(today, checkin_time)) <= grace:
                    status = "on_time"
                else:
                    status = "late_in"

            if record.check_out:
                today_check_out = localtime(record.check_out).strftime("%H:%M")
                out_time = record.check_out.time()
                if out_time < (datetime.combine(today, checkout_time) - grace).time():
                    status = "early_out"
                else:
                    status = "valid_out"

        data.append({
            "id": emp.id,
            "name": emp.name,
            "today_check_in": today_check_in,
            "today_check_out": today_check_out,
            "status": status
        })

    return render(request, "attendance_app/employee_list.html", {"employees": data})


# attendance_app/views.py
from calendar import Calendar
from datetime import date
from django.shortcuts import get_object_or_404, render
from .models import Member, Attendance

WEEKEND = {5, 6}  # 5=Saturday, 6=Sunday  (Python weekday: Mon=0)

def _six_weeks(cal, year, month):
    """Always return exactly 6 weeks (lists of 7 dates) for stable table columns."""
    weeks = cal.monthdatescalendar(year, month)  # 4..6 weeks
    while len(weeks) < 6:
        # pad with a trailing empty week using next month dates
        last_day = weeks[-1][-1]
        next_week = [last_day]  # dummy start; we'll advance by 1 day
        # build 7-day sequence continuing from last_day + 1
        next_week = []
        d = last_day
        for _ in range(7):
            d = d.replace(day=d.day)  # no-op, just clarity
        # simpler: reuse calendar from library to keep continuity:
        # but easier is to duplicate last week; UI will blank out non-month days anyway.
        weeks.append(weeks[-1])
        break
    # If more than 6 (rare), trim to 6 to keep fixed width
    return weeks[:6]

def yearly_attendance(request, member_id):
    yr = int(request.GET.get("year", date.today().year))
    member = get_object_or_404(Member, pk=member_id)

    # Preload all Attendance dates for this member & year
    att_qs = Attendance.objects.filter(member=member, date__year=yr).only("date")
    present_days = {a.date for a in att_qs}

    cal = Calendar(firstweekday=6)  # Sunday start like your sample
    months = []

    for m in range(1, 13):
        weeks = cal.monthdatescalendar(yr, m)
        # normalize to exactly 6 weeks for a stable grid (header is 6×7)
        if len(weeks) < 6:
            # pad with extra blank week(s)
            while len(weeks) < 6:
                weeks.append([weeks[-1][-1] for _ in range(7)])
        elif len(weeks) > 6:
            weeks = weeks[:6]

        matrix = []
        for week in weeks:
            row = []
            for d in week:
                if d.month != m:
                    row.append({"blank": True})
                else:
                    status = "P" if d in present_days else "A"
                    row.append({
                        "blank": False,
                        "date": d.isoformat(),
                        "day": d.day,
                        "weekend": d.weekday() in WEEKEND,
                        "status": status,
                        "status_label": "Present" if status == "P" else "Absent",
                    })
            matrix.append(row)

        months.append({
            "name": date(yr, m, 1).strftime("%B"),
            "weeks": matrix,  # exactly 6 weeks × 7 days
        })

    # Key stats (simple, since we only have Present/Absent)
    working_days = len(present_days)
    stats = {
        "leave_days": 0,
        "working_days": working_days,
        "sick_days": 0,
        "vacation_days": 0,
        "bereavement_days": 0,
        "other_days": 0,
    }

    year_choices = list(range(yr - 2, yr + 3))

    return render(request, "attendance_app/employee_yearly_log.html", {
        "employee": member,      # template expects 'employee'
        "year": yr,
        "year_choices": year_choices,
        "months": months,
        "stats": stats,
    })

