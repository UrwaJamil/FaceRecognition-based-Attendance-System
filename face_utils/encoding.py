import face_recognition

def get_face_encoding(image_path):
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image, model="hog",number_of_times_to_upsample=2)
    encodings = face_recognition.face_encodings(image, face_locations)
    print(f"🔍 {len(encodings)} faces detected")  
    return encodings
