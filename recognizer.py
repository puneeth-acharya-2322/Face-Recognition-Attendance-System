import cv2 as cv
import face_recognition
import numpy as np
import csv
import os
from datetime import datetime,timedelta
from face_encoding import load_face_encodings
from db import  attendance, subject, student
import time


def start_recognize(subcode,subname):
    cap=cv.VideoCapture(0)
    cap.set(3,600)
    cap.set(4,610)

    subcode="AI101"
    subname="AI"
    folderPath="Resources/Modes"
    modePath=os.listdir(folderPath)
    imgList=[]

    for path in modePath:
        imgList.append(cv.imread(os.path.join(folderPath,path)))

    IMAGE_PATH = "FacePhoto"
    subject.update_one({"subject_code":subcode},{"$set":{"subject_name":subname},"$inc": {"total_classes": 1}},upsert=True)
    encodings_list,names_list,regno_list=load_face_encodings(IMAGE_PATH)
    people=list(zip(names_list,regno_list))
    print("\nTotal Encoded Faces:", len(encodings_list))

    face_location=[]
    face_encoding=[]
    face_names=[]
    face_regno=[]
    s=True
    now=datetime.now()
    current_date=now.strftime("%Y-%m-%d")

   
    modeType=0
    counter=0
    studInfo=None
    subinfo=None

    resized_imgList = [cv.resize(img, (270, 540)) for img in imgList]


    while s:
        isTrue, frame = cap.read()
        small_frame = cv.resize(frame, (0, 0), fx=0.14, fy=0.14)

        rgb_small_frame = cv.cvtColor(small_frame, cv.COLOR_BGR2RGB)
        name = "Unknown"
        regno="Unknown"
        if s:
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            face_names = []
            face_regno=[]
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(encodings_list, face_encoding)

                face_distances = face_recognition.face_distance(encodings_list, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name=names_list[best_match_index]
                    regno=regno_list[best_match_index]
                    face_names.append(name)
                    face_regno.append(regno)

                    
                    if counter == 0:
                        counter = 1
                        modeType=1
                    

                    if (name,regno) in people:
                        people.remove((name,regno))
                        print(name,regno)
                        current_time = time.time()
                        current_date = datetime.now().strftime("%Y-%m-%d")
                        attendance.insert_one({"name":name, "regno":regno,"subject_code":subcode, "time":current_time, "date":current_date})

                        record=student.find_one({"regno":regno,"subjects.subject_code":subcode})
                        if record:
                            student.update_one({"regno":regno,"subjects.subject_code":subcode},{"$inc": {"subjects.$.attended_classes": 1}})
                        else:
                            student.update_one({"regno":regno},{"$set": {"name": name},"$push": {"subjects":{"subject_code":subcode,"attended_classes": 1}}},upsert=True)
                        

        haar_cascade = cv.CascadeClassifier('haar_face.xml')
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        faces = haar_cascade.detectMultiScale(gray, 1.1, 8)
        for (x, y, w, h) in faces:
            if name == "Unknown":
                cv.rectangle(frame, (x, y), (x + w, y + h), (0,0,255), 2)
                cv.putText(frame, name+"-"+regno, (20, 20), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            else:
                cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv.putText(frame,name+"-"+regno, (20, 20), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
       

        imbg = cv.imread("Resources/backgroundimg.jpg")
        imbg = cv.resize(imbg, (920, 700))

        resized_frame = cv.resize(frame, (515, 540))  # Increase frame size
        imbg[70:70 + 540, 110:110 + 515] = resized_frame  # Adjust position accordingly
        right_panel = resized_imgList[modeType].copy()

        
        if counter > 0:
            if counter == 1:
                studInfo = student.find_one({"regno": regno},{"name": 1, "regno": 1, "subjects": {"$elemMatch": {"subject_code": subcode}}})
                subinfo = subject.find_one({"subject_code": subcode})

            if counter <= 10:
                modeType=1
                right_panel = resized_imgList[modeType].copy()
                if studInfo and "subjects" in studInfo and studInfo["subjects"]:
                    subject_info = studInfo["subjects"][0]
                    classAttended = str(subject_info.get("attended_classes", "0"))
                    cv.putText(right_panel, classAttended, (28, 58), cv.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                    cv.putText(right_panel, regno, (143, 375), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    cv.putText(right_panel, str(subinfo["subject_code"]), (143, 425), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                    (wi, h), _ = cv.getTextSize(name, cv.FONT_HERSHEY_SIMPLEX, 0.8, 1)
                    offset = (270 - wi) // 2
                    cv.putText(right_panel, name, (offset, 330), cv.FONT_HERSHEY_SIMPLEX, 0.8, (255,255, 255), 2)        

            elif 10 <= counter < 20:
                modeType = 2
                right_panel = resized_imgList[modeType].copy()

            counter += 1

            if counter >= 20:
                counter = 0
                modeType = 0

            last_seen = attendance.find_one({"regno": regno, "subject_code": subcode},sort=[("time", -1)])
            if last_seen:
                duration = time.time() - last_seen.get("time", 0)
                if 5<duration < 3000:
                    modeType=3
                    right_panel = resized_imgList[modeType].copy()
                    cv.putText(right_panel, regno, (offset, 200), cv.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)      
                    
        
        imbg[70:70 + 540, 635:635 + 270] = right_panel 
        cv.imshow('FaceLog  /"Press ( x ) to Terminate', imbg)

        if cv.waitKey(1) & 0xFF == ord('x'):
            break
    cap.release()
    cv.destroyAllWindows()
