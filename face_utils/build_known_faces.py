import os
import django
import face_recognition
import pickle

# Step 1: Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "face_attendance.settings")  # ✅ Your project name
django.setup()

# Step 2: Import Django model
from attendance_app.models import Member  # ✅ Your app name

def build_known_faces():
    # Step 3: Prepare encodings and members list
    known_encodings = []
    member_ids = []

    members = Member.objects.exclude(encoding=None)

    for member in members:
        if member.face_file:
            try:
                image_path = member.face_file.path
                image = face_recognition.load_image_file(image_path)
                encodings = face_recognition.face_encodings(image)

                if encodings:
                    known_encodings.append(encodings[0])
                    member_ids.append(member.id)
                    print(f"[+] Encoded: {member.name}")
                else:
                    print(f"[!] No face found in: {member.name}")
            except Exception as e:
                print(f"[X] Error processing {member.name}: {str(e)}")

    # Step 4: Save encodings to file
    data = {
        'encodings': known_encodings,
        'members': member_ids
    }

    with open('known_faces.pkl', 'wb') as f:
        pickle.dump(data, f)

    print(f"[INFO] Encoded {len(known_encodings)} face(s)")
