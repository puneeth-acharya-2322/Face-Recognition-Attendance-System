import cv2 as cv
import os

def adding_face(name,regno):
    dir = "FacePhoto"
    if not os.path.exists(dir):
        os.mkdir(dir)

    filename = f"{name}_{regno}.jpg"
    filepath = os.path.join(dir, filename)

    cap = cv.VideoCapture(0)
    print("Press SPACEBAR to capture image or ESC to cancel.")

    captured = False

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture video.")
            break

        
        cv.imshow("ADDING FACE - Press SPACE to capture, ESC to exit", frame)
        key = cv.waitKey(1)

        if key % 256 == 27:  #Esc
                captured=False
                break

        elif key % 256 == 32:  # SPACE
            cv.imwrite(filepath, frame)
            print(f"Image saved: {filepath}")
            captured = True
            break

    cap.release()
    cv.destroyAllWindows()

    return captured
