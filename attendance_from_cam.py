import cv2
import os

# Load the face classifier
face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def face_cropped(img):

    student_folder = os.path.join("StudentPresent")
    if not os.path.exists(student_folder):
        os.makedirs(student_folder)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Detect faces in the image
    faces = face_classifier.detectMultiScale(gray, 1.2, 5)

    # Initialize img_id
    img_id = 0

    # Iterate through detected faces
    for (x, y, w, h) in faces:
        # Crop the face from the original image
        cropped_face = img[y: y+h, x:x+w]

        # Resize the face to a common size (e.g., 200x200)
        cropped_face = cv2.resize(cropped_face, (200, 200))

        # Convert the face to grayscale
        cropped_face = cv2.cvtColor(cropped_face, cv2.COLOR_BGR2GRAY)

        # Save the face to a file
        file_path = os.path.join(student_folder, f"Student_{img_id}.jpg")
        cv2.imwrite(file_path, cropped_face)

        # Increment img_id for the next face
        img_id += 1

# Example usage:
# Replace 'your_image_path.jpg' with the actual path to your image
image_path = 'IMG_3877.HEIC.jpg'


# Read the image
img = cv2.imread(image_path)

# Call the face_cropped function to detect and save faces
face_cropped(img)
