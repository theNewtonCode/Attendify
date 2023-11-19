import os
import cv2
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask import request, session, redirect, url_for, flash
from flask_mysqldb import MySQL
from database_details import dbhost, dbuser, dbpassword
from datetime import datetime



app = Flask(__name__)
app.secret_key = 'attendify2023'
socketio = SocketIO(app)

app.config['MYSQL_HOST'] = dbhost
app.config['MYSQL_USER'] = dbuser
app.config['MYSQL_PASSWORD'] = dbpassword
app.config['MYSQL_DB'] = 'attendify'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

@app.route('/loginpage', methods=['POST', 'GET'])
def loginpage():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        cur.close()

        if user:
            # Successful login, store user information in session
            session['user_name'] = user['name']
            session['username'] = user['username']
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login failed. Check your username and password.', 'danger')
            return render_template('login.html')
    return render_template('login.html')


@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        new_password = request.form['new_password']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE users SET password = %s WHERE username = %s", (new_password, session['username']))
        mysql.connection.commit()
        cur.close()

        flash('Password changed successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('change_password.html')

@app.route("/logout")
def logout():
    session.pop('user_name', None)
    return redirect(url_for('index'))


@app.route('/')
def index():
    if 'user_name' in session:
        if 'admin' in session['username']:
            admin = True
        else:
            admin = False
        return render_template('index.html', name=session['user_name'], admin=admin)
    else:
        return render_template('index.html', name=None)
    
    
@app.route("/about")
def about():
    if 'user_name' in session:
        return render_template('about.html', name=session['user_name'])
    else:
        return redirect(url_for('loginpage'))

@app.route('/addstudent')
def addstudent():
    return render_template('addStudent.html')

@app.route('/addfaculty')
def addfaculty():
    return render_template('addfaculty.html')

@app.route('/facultyprofile')
def facultyprofile():
    if 'user_name' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM faculties WHERE username = %s", (session['username'],))
        faculty = cur.fetchone()
        print("faculty", faculty)
        cur.close()
        if faculty:
            # Retrieve class details for the faculty
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM class_details WHERE faculty_username = %s", (session['username'],))
            class_details = cur.fetchall()
            cur.close()

            timings = [cd['class_timing'] for cd in class_details]
            classrooms = [cd['classroom'] for cd in class_details]
            batches = [cd['batch_name'] for cd in class_details]
            years = [cd['year'] for cd in class_details]
            groups = [cd['grp'] for cd in class_details]
            class_types = [cd['class_type'] for cd in class_details]
            

            currentclasstime = None

            # Retrieve current time
            current_time = datetime.now().time()

            # Iterate through timings to find the closest one to the current time
            for timing in timings:
                if currentclasstime is None or abs((timing.hour * 60 + timing.minute) - (current_time.hour * 60 + current_time.minute)) < abs((currentclasstime.hour * 60 + currentclasstime.minute) - (current_time.hour * 60 + current_time.minute)):
                    currentclasstime = timing
        return render_template('faculty.html', name =faculty['name'],  email = faculty['email'], depart = faculty['depart'], timings=timings, classrooms=classrooms, batches=batches, groups=groups, class_types=class_types)
    
    return render_template('faculty.html')

@app.route('/Adminhome')
def admin():
    return render_template('Admin.html')

@app.route('/showattendance')
def showattendance():
    return render_template('showattendance.html')

@app.route('/collectdataset')
def collectdataset():
    return render_template('collectimages.html')

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
            cv2.imwrite(file_path, face)

        if cv2.waitKey(1) == 15 or int(img_id) == 100:
            break

    cap.release()
    cv2.destroyAllWindows()
    # print("Dataset Creation Completed")


@socketio.on('enrolment')
def handle_enrolment(enrolment):
    gen_dataset(enrolment)
    emit('message', 'Dataset Creation Completed')

if __name__ == '__main__':
    socketio.run(app, debug=True)
