import os
import cv2
import csv
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask import request, session, redirect, url_for, flash
from flask_mysqldb import MySQL
from database_details import dbhost, dbuser, dbpassword
from datetime import datetime, timedelta
from attendance_from_cam import capture_images, face_cropped_from_list, recognize_faces
from attendify_model import FaceRecognitionModel



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

students_path = "Attendify/Students"  # Replace with the actual path to the "students" directory

@app.route('/addfaculty')
def addfaculty():
    return render_template('./addfaculty.html')

@app.route('/addstudent', methods=['POST', 'GET'])
def addstudent():
   if 'user_name' in session:
        if request.method == 'POST':
        # Extract form data
            student_id = request.form['studentID'].upper()
            name = request.form['Name'].upper()
            year = request.form['year']
            group = request.form['group'].upper()
            batch = request.form['batch'].upper()
            reg_face = False

            if os.path.exists(students_path):
    # Get the list of folders inside the "students" directory
                student_folders = [folder for folder in os.listdir(students_path) if os.path.isdir(os.path.join(students_path, folder))]

                if(student_id in student_folders):
                    reg_face = True

            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO students (student_id, name, year, student_group, batch, reg_face) VALUES (%s, %s, %s, %s, %s, %s)",
                        (student_id, name, year, group, batch, reg_face))
            mysql.connection.commit()
            cur.close()
        return render_template('addStudent.html')
   else:
       return redirect(url_for('index'))

@app.route('/addtt', methods=['POST'])
def add_timetable():
    if request.method == 'POST':
        faculty_username = request.form['facultyID']  # You need to get the faculty username from somewhere
        class_timing = request.form['time']
        classroom = request.form['courseid']
        batch_name = request.form['batch']
        year = request.form['year']
        grp = request.form['group']
        class_type = request.form['teachtype']

        # Insert data into the database
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO class_details (faculty_username, class_timing, classroom, batch_name, year, grp, class_type) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                       (faculty_username, class_timing, classroom, batch_name, year, grp, class_type))

        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('addfaculty'))

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
            

            # Assuming currentclasstime and second_closest_classtime are initially set to None
            currentclasstime = None
            second_closest_classtime = None

            # Retrieve current time
            current_time = datetime.now().time()
            # Convert current_time to timedelta for comparison
            current_time_delta = timedelta(hours=current_time.hour, minutes=current_time.minute)


            # Iterate through timings to find the closest and second closest timings to the current time
            # Iterate through timings to find the closest and second closest timings to the current time
            for timing in timings:
                if currentclasstime is None or abs(timing.total_seconds() - current_time_delta.total_seconds()) < abs(currentclasstime.total_seconds() - current_time_delta.total_seconds()):
                    second_closest_classtime = currentclasstime
                    currentclasstime = timing
                elif second_closest_classtime is None or abs(timing.total_seconds() - current_time_delta.total_seconds()) < abs(second_closest_classtime.total_seconds() - current_time_delta.total_seconds()):
                    second_closest_classtime = timing


            print(currentclasstime)
            print(second_closest_classtime)
        return render_template('faculty.html', name =faculty['name'],  email = faculty['email'], depart = faculty['depart'], timings=timings, classrooms=classrooms, batches=batches, groups=groups, class_types=class_types, currentclasstime= currentclasstime, nextclasstime=second_closest_classtime)
    
    return render_template('faculty.html')

@app.route('/Adminhome')
def admin():
    if 'user_name' in session:
        if 'admin' in session['username']:
            return render_template('Admin.html', name=session['user_name'])
    return redirect(url_for('logout'))

@app.route('/modeldetails')
def modeldetails():

    if 'user_name' in session:
        if 'admin' in session['username']:
            return render_template('modeldetail.html', admin=session['user_name'])
    return redirect(url_for('loginpage'))

@app.route('/retrain')
def retrain():
    print("model training started")
    model = FaceRecognitionModel(train_data_path='Attendify/Students', test_data_path='Attendify/Students')
    model.train_model(epochs=10)
    print(model.OutputNeurons)
    return "Finished Training"

@app.route('/takeattendance', methods=['POST'])
def take_attendance():
    if 'user_name' in session:
        currentclass = request.form['currentclass']
        batches = request.form['Batches']
        classroom = request.form['classroom']
        bl = batches.split(', ')

        cur = mysql.connection.cursor()
        cur.execute("SELECT student_id FROM students WHERE batch IN (%s)" % ','.join(['%s' for _ in bl]), tuple(bl))
        students = cur.fetchall()
        cur.close()
        total_students = len(students)
        student_ids = [student['student_id'] for student in students]
        # print(student_ids)

        return render_template('takeattendance.html', currentclass=currentclass, Batches=batches, total=total_students, classroom = classroom, attdone = False)
    
    return redirect(url_for('index'))


@app.route('/captureattendance', methods=['POST'])
def captureattendance():
    if 'user_name' in session:
        # Accessing form data
        current_class_data = request.form['currentclass']
        batches_data = request.form['Batches']

        # Get the current date
        current_date = datetime.now().strftime('%Y-%m-%d')

        # Perform calculations to get student enrollment data and attendance data
        # For the purpose of this example, let's assume you have these two lists
        bl = batches_data.split(', ')
        cur = mysql.connection.cursor()
        cur.execute("SELECT student_id FROM students WHERE batch IN (%s)" % ','.join(['%s' for _ in bl]), tuple(bl))
        students = cur.fetchall()
        cur.close()

        student_ids = [student['student_id'] for student in students]
        all_students = student_ids
        url_to_capture = "http://10.12.60.98:8080//shot.jpg"
        classimages = capture_images(url=url_to_capture, interval_seconds=2, num_images=10)

        student_faces = face_cropped_from_list(classimages)
        main_list = recognize_faces(student_faces)
        print(main_list)
        flat_list = [item for sublist in main_list for item in sublist]

        # Count the occurrences of each string
        count_dict = {}
        for item in flat_list:
            count_dict[item] = count_dict.get(item, 0) + 1

        # Create a list of strings that occur more than 4 times
        present_students = [key for key, value in count_dict.items() if value > 2]
        print(present_students)
        # present_students = ['E21CSEU0130']
        total_students_data = len(present_students)

        # Create a CSV file with attendance information for each date
        csv_filename = f"{current_class_data}_{batches_data}_{current_date}.csv"
        csv_filepath = os.path.join("Attendify/attendance_files", csv_filename)

        # Check if the CSV file already exists
        csv_exists = os.path.exists(csv_filepath)

        with open(csv_filepath, mode='a', newline='') as csvfile:
            fieldnames = ['Student', current_date]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write header if the file is new
            if not csv_exists:
                writer.writeheader()

            # Write data
            for student in all_students:
                attendance_data = 1 if student in present_students else 0
                row_data = {'Student': student, current_date: attendance_data}
                writer.writerow(row_data)

        # Return a response or redirect to a success page
        return render_template('takeattendance.html', currentclass=current_class_data, Batches=batches_data, total=total_students_data, attdone=True, filepath= csv_filepath)
    return redirect(url_for('loginpage'))


@app.route('/showattendance', methods=['POST'])
def showattendance():
    if 'user_name' in session:
        # Path to the CSV file
        current_class_data = request.form['currentclass']
        batches_data = request.form['Batches']
        total_students_data = request.form['total']
        csv_filepath = request.form['filepath']

        # Read CSV file and prepare data for rendering in the template
        attendance_data = {}
        dates = []
        
        if os.path.exists(csv_filepath):
            with open(csv_filepath, mode='r') as csvfile:
                reader = csv.DictReader(csvfile)
                dates = [header for header in reader.fieldnames if header != 'Student']

                for row in reader:
                    student = row['Student']
                    attendance_values = [row[date] for date in dates]
                    attendance_data[student] = attendance_values

        return render_template('showattendance.html', attendance_data=attendance_data, dates=dates, currentclass=current_class_data,Batches =batches_data, total = total_students_data)
    return redirect(url_for('loginpage'))

@app.route('/collectdataset')
def collectdataset():
    return render_template('collectimages.html')

def gen_dataset(enrolment):
    # Create a folder with the enrolment name if it doesn't exist
    student_folder = os.path.join("Attendify/Students", enrolment)
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

        if int(img_id) == 500:
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
