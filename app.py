import os
import cv2
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')


def gen_dataset(enrolment):
    # Create a folder with the enrolment name if it doesn't exist
    student_folder = os.path.join("alexis", enrolment)
    if not os.path.exists(student_folder):
        os.makedirs(student_folder)
    else:
        # Remove existing files in the folder if it already exists
        existing_files = os.listdir(student_folder)
        for existing_file in existing_files:
            file_path = os.path.join(student_folder, existing_file)
            os.remove(file_path)

    face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def face_cropped(img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray, 1.2, 5)
        cropped_faces = []
        for (x, y, w, h) in faces:
            cropped_face = img[y: y+h, x:x+w]
            cropped_faces.append(cropped_face)
        return cropped_faces
    
    cap = cv2.VideoCapture(0)  # Change the camera index if needed
    img_id = 0

    while True:
        ret, frame = cap.read()
        faces = face_cropped(frame)
        for face in faces:
            img_id += 1
            face = cv2.resize(face, (200, 200))
            face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
            file_path = os.path.join(student_folder, f"{enrolment}.{img_id}.jpg")
            # cv2.putText(face, str(img_id), (40, 40), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 2)
            # cv2.imshow("Cropped_Face", face)
            cv2.imwrite(file_path, face)

        if cv2.waitKey(1) == 15 or int(img_id) == 100:
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Dataset Creation Completed")

@socketio.on('enrolment')
def handle_enrolment(enrolment):
    gen_dataset(enrolment)
    emit('message', 'Dataset Creation Completed')

if __name__ == '__main__':
    socketio.run(app, debug=True)
