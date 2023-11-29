# Introduction
"Attendify" is an idea, an attendance tracking system designed to revolutionize traditional methods in educational institutions. Leveraging facial recognition technology, this system offers a contactless, accurate, and secure solution to address challenges faced by outdated attendance tracking systems. By actively promoting regular attendance, Attendify not only mitigates immediate issues but also adapts to the evolving educational landscape, ensuring a seamless and productive learning experience.

Challenges Addressed:
Outdated Attendance Methods: Conventional manual attendance tracking is vulnerable to manipulation, leading to inaccurate records and disengagement from classes.

Reduced Accountability: Exploitation of manual systems results in reduced accountability, disruptive behaviors, and an overall negative impact on the learning environment.

Post-Pandemic Challenges: Traditional attendance methods proved insufficient during the COVID-19 pandemic, highlighting the need for contactless alternatives to ensure the health and safety of students and staff.

Need for Advanced Solutions: Educational bodies emphasize the urgency of innovative attendance management solutions to address critical issues.

Solution Overview
"Attendify" addresses these challenges by introducing a facial recognition-based attendance tracking system. It takes attendance randomly and repeatedly throughout a class, encouraging continuous and active participation. If students disengage, they risk missing these sporadic checks, serving as a deterrent against attendance manipulation.

Incorporating facial recognition technology not only enhances accuracy but also fosters a culture of regular attendance, contributing to improved academic performance and graduation rates. Moreover, Attendify is adaptable to the evolving needs of educational institutions, aligning with the increasing role of technology in education.


# Working
So how Attendify works or how I planned its working is a totally unique idea, it was planned to prevent proxy, bunking, contact, and make the future of students better.
So, the web app, has two kinds of logins: 
•	The Admin: who has access to register the students and their faces, retrain the model once the students are registered, and also can add timetable for faculties, and 
•	The Faculty: who is responsible for taking the attendance, the faculty has access to their time table, which tells them their current and next classes, they have the access to take attendance in the present class only, the faculty can also have a live of the camera, and when the attendance stops, they can view the attendance in table for that day.
The attendance in stored in form of csv files for that day for that particular class.
The main database of the application is MySQL, which stores all the necessary info like the students belonging to which batch, group, year etc, the login details, the faculty time tables, etc.
The face is registered by taking 500 images (which can be changed) of the student within a span of 20-30 seconds, where the face of the student is cropped and resized into 64x64 pixels image for easy and fast computation, and storage. Over these images the CNN model is then trained, and is updated.
For attendance in the class, the camera (for now it’s a smartphone webcam) is set to take multiple images at certain time intervals, lets say for a class of 40 mins 10 images are taken over 4 mins intervals, and then those images undergo the face detection, and recognition, through our trained model, which the predicts the students enrolment ID. Now any student who is present above a threshold number of times let’s say 4 out of 10 times, they are  marked 1 or present else 0 or absent, this is done for preventing bunking and errors in the system.
