
---

# Attendify

**Introduction**

"Attendify" is an innovative attendance tracking system designed to revolutionize traditional methods in educational institutions. Leveraging cutting-edge technologies such as Python, Flask, HTML, CSS, JavaScript, CNN (Convolutional Neural Network), and MySQL, Attendify offers a contactless, accurate, and secure solution to address challenges faced by outdated attendance tracking systems.

**Challenges Addressed**

1. **Outdated Attendance Methods:** Conventional manual attendance tracking is vulnerable to manipulation, leading to inaccurate records and disengagement from classes.

2. **Reduced Accountability:** Exploitation of manual systems results in reduced accountability, disruptive behaviors, and an overall negative impact on the learning environment.

3. **Post-Pandemic Challenges:** Traditional attendance methods proved insufficient during the COVID-19 pandemic, highlighting the need for contactless alternatives to ensure the health and safety of students and staff.

4. **Need for Advanced Solutions:** Educational bodies emphasize the urgency of innovative attendance management solutions to address critical issues.

**Solution Overview**

"Attendify" addresses these challenges by introducing a facial recognition-based attendance tracking system. It takes attendance randomly and repeatedly throughout a class, encouraging continuous and active participation. If students disengage, they risk missing these sporadic checks, serving as a deterrent against attendance manipulation.

Incorporating facial recognition technology not only enhances accuracy but also fosters a culture of regular attendance, contributing to improved academic performance and graduation rates. Moreover, Attendify is adaptable to the evolving needs of educational institutions, aligning with the increasing role of technology in education.

**Working**

Attendify operates with two types of logins:

- **Admin:** Responsible for registering students and their faces, retraining the model, and managing faculty timetables.
  
- **Faculty:** Responsible for taking attendance, accessing their timetable, and viewing attendance records. Faculty members can also access a live camera feed during attendance and review attendance tables.

The main database is powered by MySQL, storing essential information such as student details, login credentials, faculty timetables, etc.

The facial recognition process involves registering a student's face by capturing 500 images within a specified timeframe. These images are cropped and resized into 64x64 pixels for efficient computation and storage. A CNN model is then trained on these images, continually updating to improve accuracy.

During a class, the system captures multiple images at specific intervals using a smartphone webcam. These images undergo face detection and recognition through the trained CNN model. Students present above a predefined threshold (e.g., 4 out of 10 times) are marked as present; otherwise, they are marked as absent, preventing bunking and minimizing errors in the system.

---

**Dependencies:**
- Python
- Flask
- HTML
- CSS
- JavaScript
- CNN (Convolutional Neural Network)
- MySQL

**Installation:**
1. Clone the repository.
2. Install required dependencies using `pip install -r requirements.txt`.
3. Set up the MySQL database with the provided schema.
4. Configure the application by updating the necessary settings.
5. Run the Flask application.

---

Feel free to contribute, report issues, or suggest improvements. Together, let's shape the future of attendance tracking with Attendify!

---
