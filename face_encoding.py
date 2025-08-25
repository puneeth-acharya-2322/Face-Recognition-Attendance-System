import face_recognition
import os

def load_face_encodings(image_dir):
    # Lists to store encodings and names
    encodings_list = []
    names_list = []
    regno_list=[]

    # Loop through each image file
    for filename in os.listdir(image_dir):
        if filename.endswith(('.jpg', '.png', '.jpeg')):  # Acceptable image types
            image_path = os.path.join(image_dir, filename)

            # Load image
            image = face_recognition.load_image_file(image_path)

            # Get face encodings
            encodings = face_recognition.face_encodings(image)

            # If a face was found
            if encodings:
                encodings_list.append(encodings[0])  # Add the encoding
                namewithreg = os.path.splitext(filename)[0]  # Get filename without extension
                name,regno=namewithreg.split("_")
                names_list.append(name)
                regno_list.append(regno)
                print(f"Encoded: {filename}")
            else:
                print(f"No face found in: {filename}")
    return encodings_list, names_list ,regno_list
