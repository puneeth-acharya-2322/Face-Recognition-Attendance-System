from flask import Flask, render_template, request,redirect,session,url_for
from recognizer import start_recognize  # direct import
from add_face import adding_face
from db import student,attendance,subject
from datetime import datetime,timedelta
from urllib.parse import urlencode

app = Flask(__name__)
app.secret_key = "f4c3_r3c0gniti0n"

@app.route("/")
def hello_world():
    return render_template("index.html")



@app.route('/recognize', methods=['POST'])
def recognize():
    subject_code = request.form.get("subject_code")
    subject_name = request.form.get("subject_name")
    if subject_code and subject_name:
        start_recognize(subject_code,subject_name)  # Will block until 'x' is pressed
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    error = {}
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username != "admin":
            error["username"] = "Invalid username"
        if password != "admin123":
            error["password"] = "Incorrect password"
        if not error:
            session['admin_logged_in'] = True
            return redirect("/admin")
        return render_template("login.html", error=error)
    return render_template("login.html", error=error)


@app.route("/admin")
def admin_dashboard():
    if not session.get("admin_logged_in"):
        return redirect("/login")

    # Dashboard stats
    total_students = student.count_documents({})
    total_subjects = subject.count_documents({})
    today_attendance = attendance.count_documents({
        "date": datetime.now().strftime("%Y-%m-%d")
    })

    # Weekly attendance bar chart
    today = datetime.now()
    week_labels = []
    attendance_counts = []

    for i in range(6, -1, -1):  # Last 7 days
        day = today - timedelta(days=i)
        date_str = day.strftime("%Y-%m-%d")
        day_label = day.strftime("%a")
        count = len(attendance.distinct("regno", {"date": date_str}))
        attendance_counts.append(count)
        week_labels.append(day_label)

    # Subject-wise pie chart
    subjects = subject.find()
    pie_labels = []
    pie_values = []
    for sub in subjects:
        pie_labels.append(sub["subject_code"])
        pie_values.append(sub.get("total_classes", 0))

    subject_classes = {}
    for s in subject.find():
        subject_classes[s["subject_name"]] = s.get("total_classes", 0)
    
    attendance_data = list(attendance.find().sort("date", -1))

    return render_template("admin.html",
                           total_students=total_students,
                           total_subjects=total_subjects,
                           today_attendance=today_attendance,
                           week_labels=week_labels,
                           attendance_counts=attendance_counts,
                           pie_labels=pie_labels,
                           pie_values=pie_values,
                           subject_classes=subject_classes,
                           attendance_data=attendance_data)

@app.route("/studentface",methods=["POST"])
def studentface():
    name = request.form.get("sname")
    regno = request.form.get("rollno")
    result = False
    if name and regno:
        result=adding_face(name,regno)  
    query = urlencode({"face_saved": str(result).lower()})  # 'true' or 'false'
    return redirect(f"{url_for('admin_dashboard')}?{query}")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
