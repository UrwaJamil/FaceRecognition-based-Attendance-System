import datetime
from django.utils import timezone
from attendance_app.models import Attendance, RecognitionLog
from django.utils.timezone import localtime, now


def mark_attendance(member, camera=None, confidence=1.0):
    today = datetime.date.today()
    current_time = localtime(now())

    attendance, created = Attendance.objects.get_or_create(member=member, date=today)

    # ✅ Step 1: Agar check_in nahi hai, to pehli dafa set karo
    if not attendance.check_in:
        attendance.check_in = current_time
        attendance.save()

    # ✅ Step 2: Agar check_in hai aur check_out empty hai → abhi checkout mat karo
    # Bas "present" consider karo, ignore kar do
    elif attendance.check_in and not attendance.check_out:
        # yahan kuch nahi karna, bas skip karo
        pass

    # ✅ Optional Step 3: Agar tum chahte ho ke checkout ho after certain hours
    # Example: agar banda dobara detect ho after 4 ghante
    elif attendance.check_in and not attendance.check_out:
        time_diff = (now - attendance.check_in).total_seconds() / 3600
        if time_diff > 4:  # 4 hours baad consider as checkout
            attendance.check_out = current_time
            attendance.save()

    # ✅ Recognition log har dafa create kar do
    RecognitionLog.objects.create(
        member=member,
        recognized=True,
        camera=camera,
        confidence=confidence
    )
    return created
