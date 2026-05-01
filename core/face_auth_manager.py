import os, time, json
import cv2
import numpy as np

class FaceAuthManager:
    def __init__(self, auth_dir="auth_faces", model_file="auth_model.yml", labels_file="auth_labels.json"):
        self.auth_dir = auth_dir
        self.model_file = model_file
        self.labels_file = labels_file
        os.makedirs(self.auth_dir, exist_ok=True)

        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

        if not hasattr(cv2, "face"):
            raise RuntimeError("cv2.face missing. Install opencv-contrib-python.")

        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.label_to_name = {}
        self.trained = False

        # Try load persisted model
        self.load_model()

    def _extract_face(self, frame_bgr):
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.2, 5)
        if len(faces) == 0:
            return None
        x, y, w, h = max(faces, key=lambda b: b[2] * b[3])
        face = gray[y:y+h, x:x+w]
        face = cv2.resize(face, (160, 160))
        return face

    def enroll_from_frame(self, name: str, frame_bgr) -> bool:
        face = self._extract_face(frame_bgr)
        if face is None:
            return False
        user_dir = os.path.join(self.auth_dir, name)
        os.makedirs(user_dir, exist_ok=True)
        fn = os.path.join(user_dir, f"{int(time.time()*1000)}.jpg")
        cv2.imwrite(fn, face)
        return True

    def retrain(self) -> bool:
        faces, labels = [], []
        self.label_to_name = {}
        label_id = 0

        for person_name in os.listdir(self.auth_dir):
            person_path = os.path.join(self.auth_dir, person_name)
            if not os.path.isdir(person_path):
                continue

            self.label_to_name[label_id] = person_name

            for fn in os.listdir(person_path):
                if not fn.lower().endswith((".jpg", ".jpeg", ".png")):
                    continue
                img = cv2.imread(os.path.join(person_path, fn), cv2.IMREAD_GRAYSCALE)
                if img is None:
                    continue
                img = cv2.resize(img, (160, 160))
                faces.append(img)
                labels.append(label_id)

            label_id += 1

        if len(faces) < 5:
            self.trained = False
            return False

        self.recognizer.train(faces, np.array(labels))
        self.trained = True
        self.save_model()
        return True

    def recognize(self, frame_bgr, threshold=70):
        if not self.trained:
            return (False, "UNTRAINED", None)

        face = self._extract_face(frame_bgr)
        if face is None:
            return (False, "NO_FACE", None)

        label, conf = self.recognizer.predict(face)
        if conf <= threshold and label in self.label_to_name:
            return (True, self.label_to_name[label], conf)

        return (False, "UNKNOWN", conf)

    def save_model(self):
        try:
            self.recognizer.write(self.model_file)
            with open(self.labels_file, "w", encoding="utf-8") as f:
                json.dump(self.label_to_name, f)
        except Exception:
            pass

    def load_model(self):
        if not (os.path.exists(self.model_file) and os.path.exists(self.labels_file)):
            return False
        try:
            self.recognizer.read(self.model_file)
            with open(self.labels_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.label_to_name = {int(k): v for k, v in data.items()}
            self.trained = True
            return True
        except Exception:
            self.trained = False
            return False
