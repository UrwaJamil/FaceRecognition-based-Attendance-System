import face_recognition
import numpy as np
import pickle

def load_known_faces():
    with open('known_faces.pkl', 'rb') as f:
        data = pickle.load(f)
    return data['encodings'], data['members']

def match_face(unknown_encoding, known_encodings, tolerance=0.45):
    face_distances = face_recognition.face_distance(known_encodings, unknown_encoding)
    best_match_index = np.argmin(face_distances)   # 👈 yahan se hamesha koi na koi index mil jata hai
    best_distance = face_distances[best_match_index]

    if best_distance <= tolerance:
        confidence = 1 - best_distance
        return best_match_index, confidence
    
    return None, 0.0

