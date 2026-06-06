from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import TimeTable
from student.models import AttendanceEvidence



import cv2
import base64
import numpy as np
import pickle
import face_recognition
import json
import os

from student.models import Student, Attendance
from .models import Teacher
from ultralytics import YOLO
yolo_model = YOLO("yolov8n.pt")

def clean_id(value):
    if value and value != "None" and str(value).isdigit():
        return int(value)
    return None


def teacher_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)

        if user is not None and hasattr(user, "teacher"):
            login(request, user)
            return redirect("/teacher/dashboard/")

        return render(request, "teacher/teacher_login.html", {
            "error": "Invalid credentials"
        })

    return render(request, "teacher/teacher_login.html")


@login_required
def teacher_dashboard(request):
    teacher = Teacher.objects.filter(user=request.user).first()

    if not teacher:
        return redirect("/teacher-login/")

    departments = teacher.departments.all()
    classes = teacher.classes.all()
    subjects = teacher.subjects.all()

    total_students = Student.objects.filter(
        class_name__in=classes
    ).distinct().count()

    today_attendance = Attendance.objects.filter(
        subject__in=subjects,
        timestamp__date=timezone.now().date()
    ).count()

    recent_attendance = Attendance.objects.filter(
        subject__in=subjects
    ).order_by("-timestamp")[:5]

    return render(request, "teacher/teacher_dashboard.html", {
        "teacher": teacher,
        "departments": departments,
        "classes": classes,
        "subjects": subjects,
        "total_students": total_students,
        "total_classes": classes.count(),
        "total_subjects": subjects.count(),
        "today_attendance": today_attendance,
        "recent_attendance": recent_attendance,
        "chart_labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
        "chart_data": [5, 8, 6, 10, 7, 9],
    })


@login_required
def mark_attendance(request):
    teacher = Teacher.objects.filter(user=request.user).first()

    if not teacher:
        return redirect("/teacher-login/")

    departments = teacher.departments.all()
    all_classes = teacher.classes.all()
    subjects = teacher.subjects.all()

    students = []
    selected_department = None
    selected_class = None
    selected_subject = None
    filtered_classes = all_classes

    if request.method == "POST":
        department_id = clean_id(request.POST.get("department"))
        class_id = clean_id(request.POST.get("class"))
        subject_id = clean_id(request.POST.get("subject"))

        if not department_id or not class_id or not subject_id:
            messages.error(request, "Please select department, class and subject.")
            return redirect("/teacher/mark-attendance/")

        selected_department = departments.filter(id=department_id).first()
        selected_class = all_classes.filter(id=class_id).first()
        selected_subject = subjects.filter(id=subject_id).first()

        if not selected_department or not selected_class or not selected_subject:
            messages.error(request, "Invalid selection.")
            return redirect("/teacher/mark-attendance/")

        students = Student.objects.filter(
            department=selected_department,
            class_name=selected_class
        )

        saved_count = 0

        for student in students:
            status = request.POST.get(f"status_{student.id}")

            if status in ["Present", "Absent", "Late"]:
                Attendance.objects.create(
                    student=student,
                    subject=selected_subject,
                    status=status,
                    timestamp=timezone.now()
                )
                saved_count += 1

        if saved_count == 0:
            messages.warning(request, "No students were selected.")
        else:
            messages.success(request, f"Attendance saved for {saved_count} student(s).")

        return redirect(
            f"/teacher/mark-attendance/?department={department_id}&class={class_id}&subject={subject_id}"
        )

    department_id = clean_id(request.GET.get("department"))
    class_id = clean_id(request.GET.get("class"))
    subject_id = clean_id(request.GET.get("subject"))

    if department_id:
        selected_department = departments.filter(id=department_id).first()

    if class_id:
        selected_class = all_classes.filter(id=class_id).first()

    if subject_id:
        selected_subject = subjects.filter(id=subject_id).first()

    if selected_department:
        filtered_classes = all_classes.filter(department=selected_department)

    if selected_department and selected_class and selected_subject:
        students = Student.objects.filter(
            department=selected_department,
            class_name=selected_class
        )

    return render(request, "teacher/teacher_mark_attendance.html", {
        "teacher": teacher,
        "departments": departments,
        "classes": filtered_classes,
        "subjects": subjects,
        "students": students,
        "selected_department": selected_department,
        "selected_class": selected_class,
        "selected_subject": selected_subject,
    })


@login_required
def teacher_reports(request):
    teacher = Teacher.objects.filter(user=request.user).first()

    if not teacher:
        return redirect("/teacher-login/")

    subjects = teacher.subjects.all()
    classes = teacher.classes.all()

    attendances = Attendance.objects.filter(
        subject__in=subjects
    ).order_by("-timestamp")

    subject_id = clean_id(request.GET.get("subject"))
    class_id = clean_id(request.GET.get("class"))

    if subject_id:
        attendances = attendances.filter(subject_id=subject_id)

    if class_id:
        attendances = attendances.filter(student__class_name_id=class_id)

    total = attendances.count()
    present = attendances.filter(status="Present").count()
    absent = attendances.filter(status="Absent").count()
    late = attendances.filter(status="Late").count()

    percentage = 0

    if total > 0:
        percentage = round((present / total) * 100, 2)

    return render(request, "teacher/teacher_reports.html", {
        "teacher": teacher,
        "subjects": subjects,
        "classes": classes,
        "attendances": attendances,
        "total": total,
        "present": present,
        "absent": absent,
        "late": late,
        "percentage": percentage,
        "chart_labels": ["Present", "Absent", "Late"],
        "chart_data": [present, absent, late],
    })


@login_required
def teacher_profile(request):
    teacher = Teacher.objects.filter(user=request.user).first()

    if not teacher:
        return redirect("/teacher-login/")

    if request.method == "POST":
        teacher.name = request.POST.get("name")
        teacher.phone = request.POST.get("phone")

        if request.FILES.get("profile_photo"):
            teacher.profile_photo = request.FILES.get("profile_photo")

        teacher.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("/teacher/profile/")

    return render(request, "teacher/teacher_profile.html", {
        "teacher": teacher
    })


@login_required
def teacher_settings(request):
    teacher = Teacher.objects.filter(user=request.user).first()

    if not teacher:
        return redirect("/teacher-login/")

    return render(request, "teacher/teacher_settings.html", {
        "teacher": teacher
    })


@login_required
def change_password(request):
    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if not request.user.check_password(current_password):
            messages.error(request, "Current password is incorrect")
            return redirect("/teacher/settings/")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("/teacher/settings/")

        request.user.set_password(new_password)
        request.user.save()

        update_session_auth_hash(request, request.user)

        messages.success(request, "Password updated successfully")
        return redirect("/teacher/settings/")

    return redirect("/teacher/settings/")


@csrf_exempt
def detect_faces(request):
    if request.method == "POST":
        try:
            body_data = json.loads(request.body)
            image_data = body_data.get("image")

            if not image_data:
                return JsonResponse({"faces": [], "error": "No image received"})

            if not os.path.exists("encodings.pkl"):
                return JsonResponse({"faces": [], "error": "AI model not trained"})

            format_data, imgstr = image_data.split(";base64,")
            img_bytes = base64.b64decode(imgstr)

            np_arr = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if frame is None:
                return JsonResponse({"faces": [], "error": "Invalid image"})
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            with open("encodings.pkl", "rb") as f:
                saved_data = pickle.load(f)

            known_encodings = saved_data.get("encodings", [])
            known_names = saved_data.get("names", [])

            if len(known_encodings) == 0:
                return JsonResponse({"faces": [], "error": "No trained faces found"})

            results = yolo_model.predict(
                frame,
                device=0,
                imgsz=320,
                conf=0.4,
                verbose=False
            )

            person_count = 0

            for box in results[0].boxes:
                cls_id = int(box.cls[0])

                if yolo_model.names[cls_id] == "person":
                    person_count += 1

            if person_count == 0:
                return JsonResponse({
                    "faces": [],
                    "error": "No person detected"
                })

            face_locations = face_recognition.face_locations(
                rgb_frame,
                model="hog"
            )

            face_encodings = face_recognition.face_encodings(
                rgb_frame,
                face_locations
            )

            detected_students = []

            for face_encoding in face_encodings:
                face_distances = face_recognition.face_distance(
                    known_encodings,
                    face_encoding
                )

                best_match_index = np.argmin(face_distances)
                best_distance = face_distances[best_match_index]

                name = "Unknown"

                if best_distance <= 0.50:
                    student_id = known_names[best_match_index]
                    student = Student.objects.filter(id=student_id).first()

                    if student:
                        name = student.user.first_name

                detected_students.append(name)

            return JsonResponse({
                "faces": detected_students,
                "person_count": person_count
            })

        except Exception as e:
            return JsonResponse({"faces": [], "error": str(e)})

    return JsonResponse({"faces": []})


@login_required
def teacher_logout(request):
    logout(request)
    return redirect("/teacher-login/")

@login_required
def load_teacher_data(request):

    teacher = Teacher.objects.filter(user=request.user).first()

    department_id = request.GET.get("department_id")

    classes = []
    subjects = []

    if teacher and department_id:

        classes = list(
            teacher.classes.filter(
                department_id=department_id
            ).values("id", "name")
        )

        subjects = list(
            teacher.subjects.filter(
                department_id=department_id
            ).values("id", "name")
        )

    return JsonResponse({
        "classes": classes,
        "subjects": subjects
    })

@login_required
def teacher_timetable(request):

    teacher = Teacher.objects.filter(user=request.user).first()

    if not teacher:
        return redirect("/teacher-login/")

    timetables = TimeTable.objects.filter(
        teacher=teacher
    ).select_related(
        "department",
        "class_room",
        "subject"
    ).order_by("start_time")

    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
    ]

    times = timetables.values_list(
        "start_time",
        "end_time"
    ).distinct()

    return render(request, "teacher/teacher_timetable.html", {
        "teacher": teacher,
        "timetables": timetables,
        "days": days,
        "times": times,
    })

@login_required
def edit_attendance(request, attendance_id):

    teacher = Teacher.objects.filter(
        user=request.user
    ).first()

    if not teacher:
        return redirect("/teacher-login/")

    attendance = Attendance.objects.filter(
        id=attendance_id,
        subject__in=teacher.subjects.all()
    ).first()

    if not attendance:
        messages.error(request, "Attendance record not found.")
        return redirect("/teacher/reports/")

    if request.method == "POST":
        status = request.POST.get("status")

        if status in ["Present", "Absent", "Late"]:
            attendance.status = status
            attendance.save()
            messages.success(request, "Attendance updated successfully.")
        else:
            messages.error(request, "Invalid status.")

        return redirect("/teacher/reports/")

    return render(request, "teacher/edit_attendance.html", {
        "attendance": attendance,
        "teacher": teacher
    })

@login_required
def upload_attendance_evidence(request):

    teacher = Teacher.objects.filter(user=request.user).first()

    if not teacher:
        return redirect("/teacher-login/")

    if request.method == "POST":
        subject_id = request.POST.get("subject_id")
        class_id = request.POST.get("class_id")
        photo = request.FILES.get("photo")

        if not photo:
            messages.error(request, "Please upload a class photo.")
            return redirect("/teacher/reports/")

        subject = teacher.subjects.filter(id=subject_id).first()
        class_room = teacher.classes.filter(id=class_id).first()

        if not subject or not class_room:
            messages.error(request, "Invalid class or subject.")
            return redirect("/teacher/reports/")

        AttendanceEvidence.objects.create(
            teacher=teacher,
            subject=subject,
            class_room=class_room,
            photo=photo
        )

        messages.success(request, "Class evidence photo uploaded successfully.")
        return redirect("/teacher/reports/")
    

@login_required
def view_evidence(request, attendance_id):

    attendance = Attendance.objects.get(
        id=attendance_id
    )

    evidence = AttendanceEvidence.objects.filter(
        subject=attendance.subject,
        class_room=attendance.student.class_name
    ).order_by('-uploaded_at').first()

    return render(
        request,
        "teacher/view_evidence.html",
        {
            "attendance": attendance,
            "evidence": evidence
        }
    )