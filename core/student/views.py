from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.core.files.base import ContentFile
from teacher.models import TimeTable
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from teacher.models import Teacher



import pickle
import face_recognition
import io
import os

from PIL import Image

import base64
import json
import cv2
import numpy as np

from .models import (
    Department,
    Class,
    Student,
    Attendance,
    Subject,
    StudentFace
)

from ultralytics import YOLO

yolo_model = YOLO("yolov8n.pt")

# =========================
# 🔐 LOGIN
# =========================

def student_login(request):

    if request.method == "POST":

        reg_no = request.POST.get(
            'register_number'
        )

        password = request.POST.get(
            'password'
        )

        user = authenticate(

            username=reg_no,

            password=password

        )

        if user is not None:

            login(request, user)

            return redirect(
                '/dashboard/'
            )

        else:

            return render(

                request,

                'student/student_login.html',

                {

                    'error':
                    'Invalid Register Number or Password'

                }

            )

    return render(

        request,

        'student/student_login.html'

    )


# =========================
# 📝 REGISTER
# =========================

def student_register(request):

    departments = Department.objects.all()

    classes = Class.objects.all()

    if request.method == "POST":

        name = request.POST['name']

        reg_no = request.POST[
            'register_number'
        ]

        department_id = request.POST[
            'department'
        ]

        class_id = request.POST[
            'class_name'
        ]

        password = request.POST[
            'password'
        ]

        confirm_password = request.POST[
            'confirm_password'
        ]

        if password != confirm_password:

            return render(

                request,

                'student/student_register.html',

                {

                    'error':
                    'Passwords do not match',

                    'departments':
                    departments,

                    'classes':
                    classes

                }

            )

        user = User.objects.filter(

            username=reg_no

        ).first()

        if user:

            if Student.objects.filter(

                user=user

            ).exists():

                return render(

                    request,

                    'student/student_register.html',

                    {

                        'error':
                        'Student already registered',

                        'departments':
                        departments,

                        'classes':
                        classes

                    }

                )

        else:

            user = User.objects.create_user(

                username=reg_no,

                password=password,

                first_name=name

            )

        department = Department.objects.get(
            id=department_id
        )

        class_obj = Class.objects.get(
            id=class_id
        )

        Student.objects.create(

            user=user,

            register_number=reg_no,

            department=department,

            class_name=class_obj

        )

        return redirect('/')

    return render(

        request,

        'student/student_register.html',

        {

            'departments': departments,

            'classes': classes

        }

    )


# =========================
# 🔄 LOAD CLASSES
# =========================

def load_classes(request):

    department_id = request.GET.get(
        'department_id'
    )

    classes = Class.objects.filter(

        department_id=department_id

    ).values(

        'id',

        'name'

    )

    return JsonResponse(

        list(classes),

        safe=False

    )


# =========================
# 📊 DASHBOARD
# =========================

@never_cache
@login_required
def student_dashboard(request):

    student = Student.objects.filter(
        user=request.user
    ).first()

    if not student:

        return redirect('/')

    attendance = Attendance.objects.filter(
        student=student
    )

    total = attendance.count()

    present = attendance.filter(
        status='Present'
    ).count()

    absent = attendance.filter(
        status='Absent'
    ).count()

    late = attendance.filter(
        status='Late'
    ).count()

    effective_present = (
        present + (late * 0.5)
    )

    percentage = 0

    if total > 0:

        percentage = round(

            (effective_present / total) * 100,

            2

        )

    today = timezone.now().date()

    today_attendance = Attendance.objects.filter(

        student=student,

        timestamp__date=today

    ).first()

    subjects = Subject.objects.all()

    subject_attendance = []

    for subject in subjects:

        total_subject = Attendance.objects.filter(

            student=student,

            subject=subject

        ).count()

        present_subject = Attendance.objects.filter(

            student=student,

            subject=subject,

            status='Present'

        ).count()

        percentage_subject = 0

        if total_subject > 0:

            percentage_subject = round(

                (present_subject / total_subject) * 100,

                2

            )

        subject_attendance.append({

            'subject': subject.name,

            'percentage': percentage_subject

        })

    total_faces = StudentFace.objects.filter(
        student=student
    ).count()

    recent_faces = StudentFace.objects.filter(
        student=student
    ).order_by('-id')[:6]

    return render(

        request,

        'student/student_dashboard.html',

        {

            'student': student,

            'today_attendance':
            today_attendance,

            'total': total,

            'present': present,

            'absent': absent,

            'late': late,

            'percentage': percentage,

            'subject_attendance':
            subject_attendance,

            'total_faces': total_faces,

            'recent_faces': recent_faces

        }

    )


# =========================
# 📋 ATTENDANCE
# =========================

@login_required
def student_attendance(request):

    student = Student.objects.filter(
        user=request.user
    ).first()

    if not student:

        messages.error(
            request,
            "Please login as student account."
        )

        return redirect('/')

    qs = Attendance.objects.filter(
        student=student
    ).select_related(
        'subject'
    )

    status = request.GET.get('status')

    start = request.GET.get('start')

    end = request.GET.get('end')

    if status and status != "None":

        qs = qs.filter(
            status=status
        )

    if start and start != "None":

        start_date = parse_date(start)

        if start_date:

            qs = qs.filter(
                timestamp__date__gte=start_date
            )

    if end and end != "None":

        end_date = parse_date(end)

        if end_date:

            qs = qs.filter(
                timestamp__date__lte=end_date
            )

    qs = qs.order_by('-timestamp')

    total = qs.count()

    present = qs.filter(
        status='Present'
    ).count()

    absent = qs.filter(
        status='Absent'
    ).count()

    late = qs.filter(
        status='Late'
    ).count()

    return render(

        request,

        'student/student_attendance.html',

        {

            'student': student,

            'attendance': qs,

            'total': total,

            'present': present,

            'absent': absent,

            'late': late,

            'status': status or '',

            'start': start or '',

            'end': end or '',

        }

    )

# =========================
# 👤 PROFILE
# =========================

@login_required
def student_profile(request):

    student = Student.objects.get(
        user=request.user
    )

    # =========================
    # UPDATE PROFILE
    # =========================

    if request.method == 'POST':

        request.user.first_name = request.POST.get(
            'name'
        )

        request.user.email = request.POST.get(
            'email'
        )

        student.phone = request.POST.get(
            'phone'
        )

        if request.FILES.get(
            'profile_photo'
        ):

            student.profile_photo = request.FILES.get(
                'profile_photo'
            )

        request.user.save()

        student.save()

        return redirect(
            'student_profile'
        )

    # =========================
    # ATTENDANCE
    # =========================

    attendance = Attendance.objects.filter(
        student=student
    )

    total_classes = attendance.count()

    present_count = attendance.filter(
        status='Present'
    ).count()

    absent_count = attendance.filter(
        status='Absent'
    ).count()

    late_count = attendance.filter(
        status='Late'
    ).count()

    percentage = 0

    if total_classes > 0:

        effective_present = (

            present_count +

            (late_count * 0.5)

        )

        percentage = round(

            (effective_present / total_classes) * 100,

            2

        )

    # =========================
    # FACE DATASET
    # =========================

    student_faces = StudentFace.objects.filter(
        student=student
    ).order_by('-id')

    total_faces = student_faces.count()

    recent_faces = StudentFace.objects.filter(
        student=student
    ).order_by('-id')[:12]

    latest_face = StudentFace.objects.filter(
        student=student
    ).last()

    return render(

        request,

        'student/student_profile.html',

        {

            'student': student,

            'total_classes':
            total_classes,

            'present_count':
            present_count,

            'absent_count':
            absent_count,

            'late_count':
            late_count,

            'percentage':
            percentage,

            'student_faces':
            student_faces,

            'recent_faces':
            recent_faces,

            'latest_face':
            latest_face,

            'total_faces':
            total_faces

        }

    )


# =========================
# ⚙️ SETTINGS
# =========================

@login_required
def student_settings(request):

    form = PasswordChangeForm(
        request.user
    )

    return render(

        request,

        'student/student_settings.html',

        {

            'form': form

        }

    )


# =========================
# 🔐 CHANGE PASSWORD
# =========================

@login_required
def change_password(request):

    if request.method == 'POST':

        form = PasswordChangeForm(

            request.user,

            request.POST

        )

        if form.is_valid():

            user = form.save()

            update_session_auth_hash(
                request,
                user
            )

            messages.success(

                request,

                'Password updated successfully'

            )

            return redirect('/settings/')

        else:

            for error in form.errors.values():

                messages.error(
                    request,
                    error
                )

    else:

        form = PasswordChangeForm(
            request.user
        )

    return render(

        request,

        'student/student_password_change.html',

        {

            'form': form

        }

    )


# =========================
# 📈 REPORTS
# =========================
@login_required
def student_reports(request):

    student = Student.objects.filter(
        user=request.user
    ).first()

    if not student:

        messages.error(
            request,
            "This login account is not connected to a student."
        )

        return redirect('/')

    attendance = Attendance.objects.filter(
        student=student
    ).select_related(
        'subject'
    ).order_by('-timestamp')

    total = attendance.count()

    present = attendance.filter(
        status__iexact='Present'
    ).count()

    absent = attendance.filter(
        status__iexact='Absent'
    ).count()

    late = attendance.filter(
        status__iexact='Late'
    ).count()

    # =========================
    # HALF ATTENDANCE FOR LATE
    # =========================

    effective_present = (
        present + (late * 0.5)
    )

    percentage = 0

    if total > 0:

        percentage = round(
            (effective_present / total) * 100,
            2
        )

    # =========================
    # SUBJECT WISE
    # =========================

    subject_data = []

    subjects = Subject.objects.all()

    for subject in subjects:

        subject_attendance = attendance.filter(
            subject=subject
        )

        total_subject = subject_attendance.count()

        present_subject = subject_attendance.filter(
            status='Present'
        ).count()

        late_subject = subject_attendance.filter(
            status='Late'
        ).count()

        effective_subject = (
            present_subject + (late_subject * 0.5)
        )

        subject_percentage = 0

        if total_subject > 0:

            subject_percentage = round(
                (effective_subject / total_subject) * 100,
                2
            )

            subject_data.append({

                'name': subject.name,

                'percentage': subject_percentage,

                'total': total_subject,

                'present': present_subject,

                'late': late_subject

            })

    # =========================
    # MONTHLY STATS
    # =========================

    monthly_stats = attendance.annotate(

        month=TruncMonth('timestamp')

    ).values('month').annotate(

        total=Count('id')

    ).order_by('month')

    months = []
    monthly_totals = []

    for item in monthly_stats:

        if item['month']:

            months.append(
                item['month'].strftime('%b')
            )

            monthly_totals.append(
                item['total']
            )

    # =========================
    # ATTENDANCE TREND
    # =========================

    recent_attendance = attendance[:8]

    return render(

        request,

        'student/student_reports.html',

        {

            'student': student,

            'attendance': attendance,

            'recent_attendance': recent_attendance,

            'total': total,

            'present': present,

            'absent': absent,

            'late': late,

            'effective_present': effective_present,

            'percentage': percentage,

            'subject_data': subject_data,

            'months': json.dumps(months),

            'monthly_totals': json.dumps(monthly_totals),

        }

    )

@login_required
def download_attendance_pdf(request):

    student = Student.objects.get(
        user=request.user
    )

    attendance = Attendance.objects.filter(
        student=student
    ).order_by('-timestamp')

    response = HttpResponse(
        content_type='application/pdf'
    )

    response['Content-Disposition'] = (
        'attachment; filename="attendance_report.pdf"'
    )

    doc = SimpleDocTemplate(
        response,
        pagesize=letter
    )

    styles = getSampleStyleSheet()

    elements = []

    title = Paragraph(
        f"<b>{student.user.first_name} Attendance Report</b>",
        styles['Title']
    )

    elements.append(title)
    elements.append(Spacer(1, 20))

    data = [[
        'Date',
        'Subject',
        'Status'
    ]]

    for item in attendance:

        subject_name = (
            item.subject.name
            if item.subject
            else "No Subject"
        )

        data.append([
            item.timestamp.strftime(
                "%d-%m-%Y %I:%M %p"
            ),
            subject_name,
            item.status
        ])

    table = Table(data)

    table.setStyle(TableStyle([

        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2563eb")),

        ('TEXTCOLOR', (0,0), (-1,0), colors.white),

        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),

        ('BOTTOMPADDING', (0,0), (-1,0), 12),

        ('GRID', (0,0), (-1,-1), 1, colors.grey),

        ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),

    ]))

    elements.append(table)

    doc.build(elements)

    return response

# =========================
# 📸 SAVE FACE
# =========================

from django.core.management import call_command

@login_required
def save_face(request):

    if request.method == 'POST':

        try:

            student = Student.objects.get(
                user=request.user
            )

            data = json.loads(
                request.body
            )

            image_data = data['image']

            # =========================
            # REMOVE BASE64 HEADER
            # =========================

            format, imgstr = image_data.split(
                ';base64,'
            )

            ext = format.split('/')[-1]

            # =========================
            # FILE NAME
            # =========================

            image_count = StudentFace.objects.filter(
                student=student
            ).count()

            file_name = (
                f"face_{image_count + 1}.{ext}"
            )

            # =========================
            # DECODE IMAGE
            # =========================

            img_data = base64.b64decode(
                imgstr
            )

            # =========================
            # IMAGE ARRAY
            # =========================

            nparr = np.frombuffer(

                img_data,

                np.uint8

            )

            frame = cv2.imdecode(

                nparr,

                cv2.IMREAD_COLOR
            )


            # =========================
            # BLUR DETECTION
            # =========================

            gray = cv2.cvtColor(

                frame,

                cv2.COLOR_BGR2GRAY

            )

            blur_value = cv2.Laplacian(

                gray,

                cv2.CV_64F

            ).var()

            print(f"Blur Value: {blur_value}")

            # =========================
            # ONLY REJECT VERY BLURRY
            # =========================

            if blur_value < 40:

                return JsonResponse({

                    'success': False,

                    'message':
                    'Image too blurry. '
                    'Keep camera steady.'

                })

            # =========================
            # RGB
            # =========================

            rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            # =========================
            # FACE DETECTION
            # =========================

            face_locations = face_recognition.face_locations(

                rgb,

                model='hog'
            )

            # NO FACE

            if len(face_locations) == 0:

                return JsonResponse({

                    'success': False,

                    'message':
                    'No face detected'

                })

            # MULTIPLE FACES

            if len(face_locations) > 1:

                return JsonResponse({

                    'success': False,

                    'message':
                    'Multiple faces detected'

                })

            # =========================
            # SAVE FILE
            # =========================

            file = ContentFile(

                img_data,

                name=file_name

            )

            StudentFace.objects.create(

                student=student,

                image=file

            )

            total_faces = image_count + 1

            # =========================
            # AUTO TRAIN MODEL
            # =========================

            try:

                faces = StudentFace.objects.filter(

                    student=student

                ).order_by('-id')[:20]

                # =====================
                # LOAD EXISTING MODEL
                # =====================

                known_encodings = []
                known_names = []

                if os.path.exists('encodings.pkl'):

                    with open(
                        'encodings.pkl',
                        'rb'
                    ) as f:

                        data = pickle.load(f)

                        known_encodings = data[
                            'encodings'
                        ]

                        known_names = data[
                            'names'
                        ]

                # =====================
                # REMOVE OLD ENCODINGS
                # =====================

                filtered_encodings = []
                filtered_names = []

                for encoding, name in zip(

                    known_encodings,

                    known_names

                ):

                    if str(name) != str(student.id):

                        filtered_encodings.append(
                            encoding
                        )

                        filtered_names.append(
                            name
                        )

                known_encodings = filtered_encodings
                known_names = filtered_names

                # =====================
                # TRAIN CURRENT STUDENT
                # =====================

                for face in faces:

                    try:

                        image_path = face.image.path

                        if not os.path.exists(
                            image_path
                        ):

                            continue

                        image = face_recognition.load_image_file(
                            image_path
                        )

                        face_locations = face_recognition.face_locations(

                            image,

                            model='hog'
                        )

                        if len(face_locations) != 1:

                            continue

                        encodings = face_recognition.face_encodings(

                            image,

                            face_locations,

                            num_jitters=1

                        )

                        if len(encodings) > 0:

                            known_encodings.append(
                                encodings[0]
                            )

                            known_names.append(
                                student.id
                            )

                    except:

                        continue

                # =====================
                # SAVE MODEL
                # =====================

                with open(
                    'encodings.pkl',
                    'wb'
                ) as f:

                    pickle.dump({

                        'encodings':
                        known_encodings,

                        'names':
                        known_names

                    }, f)

            except Exception as e:

                print(e)

            # =========================
            # SUCCESS
            # =========================

            return JsonResponse({

                'success': True,

                'message':
                'Face Saved & AI Trained Successfully',

                'total_faces':
                total_faces

            })

        except Exception as e:

            return JsonResponse({

                'success': False,

                'message': str(e)

            })

    return JsonResponse({

        'success': False,

        'message': 'Invalid Request'

    })


# =====================================
# 🤖 PROFESSIONAL INCREMENTAL TRAINING
# =====================================

@login_required
def finalize_training(request):

    if request.method == "POST":

        try:

            student = Student.objects.get(
                user=request.user
            )

            # =========================
            # USE ONLY LATEST 5 IMAGES
            # =========================

            faces = StudentFace.objects.filter(

                student=student

            ).order_by('-id')[:20]

            # =========================
            # NO DATASET
            # =========================

            if not faces.exists():

                return JsonResponse({

                    'success': False,

                    'message':
                    'No face dataset found'

                })

            # =========================
            # LOAD EXISTING MODEL
            # =========================

            known_encodings = []
            known_names = []

            if os.path.exists('encodings.pkl'):

                with open(
                    'encodings.pkl',
                    'rb'
                ) as f:

                    data = pickle.load(f)

                    known_encodings = data[
                        'encodings'
                    ]

                    known_names = data[
                        'names'
                    ]

            # =========================
            # REMOVE OLD ENCODINGS
            # =========================

            filtered_encodings = []
            filtered_names = []

            for encoding, name in zip(

                known_encodings,

                known_names

            ):

                if str(name) != str(student.id):

                    filtered_encodings.append(
                        encoding
                    )

                    filtered_names.append(
                        name
                    )

            known_encodings = filtered_encodings
            known_names = filtered_names

            total_encoded = 0
            total_skipped = 0

            # =========================
            # TRAIN CURRENT STUDENT
            # =========================

            for face in faces:

                try:

                    image_path = face.image.path

                    # =========================
                    # FILE EXISTS
                    # =========================

                    if not os.path.exists(
                        image_path
                    ):

                        total_skipped += 1

                        continue

                    # =========================
                    # LOAD IMAGE
                    # =========================

                    image = face_recognition.load_image_file(
                        image_path
                    )

                    # =========================
                    # KEEP ORIGINAL IMAGE
                    # =========================

                    small_image = image

                    # =========================
                    # FACE DETECTION
                    # =========================

                    face_locations = face_recognition.face_locations(

                        small_image,

                        model='hog'

                    )

                    print(

                        f"Faces detected: "
                        f"{len(face_locations)}"

                    )

                    # =========================
                    # NO FACE
                    # =========================

                    if len(face_locations) == 0:

                        total_skipped += 1

                        continue

                    # =========================
                    # MULTIPLE FACE
                    # =========================

                    if len(face_locations) > 1:

                        total_skipped += 1

                        continue

                    # =========================
                    # FACE ENCODINGS
                    # =========================

                    encodings = face_recognition.face_encodings(

                        small_image,

                        face_locations,

                        num_jitters=1

                    )

                    # =========================
                    # SAVE ENCODING
                    # =========================

                    if len(encodings) > 0:

                        known_encodings.append(
                            encodings[0]
                        )

                        known_names.append(
                            student.id
                        )

                        total_encoded += 1

                        print(

                            f"✅ Encoded: "
                            f"{student.user.first_name}"

                        )

                    else:

                        total_skipped += 1

                except Exception as e:

                    print(e)

                    total_skipped += 1

            # =========================
            # SAVE MODEL
            # =========================

            with open(
                'encodings.pkl',
                'wb'
            ) as f:

                pickle.dump({

                    'encodings':
                    known_encodings,

                    'names':
                    known_names

                }, f)

            # =========================
            # SUCCESS
            # =========================

            return JsonResponse({

                'success': True,

                'message':
                'AI Model Updated Successfully',

                'total_encoded':
                total_encoded,

                'total_skipped':
                total_skipped

            })

        except Exception as e:

            return JsonResponse({

                'success': False,

                'message': str(e)

            })

    return JsonResponse({

        'success': False

    })


@csrf_exempt
@login_required
def detect_faces(request):

    if request.method != "POST":
        return JsonResponse({"boxes": []})

    try:
        data = json.loads(request.body)

        image_data = data.get("image")

        format, imgstr = image_data.split(";base64,")

        image_bytes = base64.b64decode(imgstr)

        np_arr = np.frombuffer(
            image_bytes,
            np.uint8
        )

        frame = cv2.imdecode(
            np_arr,
            cv2.IMREAD_COLOR
        )

        results = yolo_model.predict(
            frame,
            device=0,
            imgsz=640,
            conf=0.35,
            verbose=False
        )

        boxes = []

        for box in results[0].boxes:

            cls_id = int(box.cls[0])

            if yolo_model.names[cls_id] != "person":
                continue

            x1, y1, x2, y2 = map(
                int,
                box.xyxy[0]
            )

            boxes.append({
                "top": y1,
                "right": x2,
                "bottom": y2,
                "left": x1
            })

        return JsonResponse({
            "boxes": boxes
        })

    except Exception as e:

        return JsonResponse({
            "boxes": [],
            "error": str(e)
        })
# =====================================
# 🤖 PROFESSIONAL FACE CROP RECOGNITION
# =====================================

@login_required
def recognize_group(request):

    if request.method != 'POST':

        return JsonResponse({

            'success': False,

            'message': 'Invalid Request'

        })

    try:

        data = json.loads(request.body)

        face_images = data.get('faces', [])

        subject_id = data.get('subject_id')
        class_id = data.get('class_id')
        if not face_images:

            return JsonResponse({

                'success': False,

                'message': 'No face images received'

            })

        # =========================
        # SUBJECT
        # =========================

        subject = None

        if subject_id:

            try:

                subject = Subject.objects.get(
                    id=subject_id
                )

            except:

                subject = None

        # =========================
        # LOAD MODEL
        # =========================

        if not os.path.exists('encodings.pkl'):

            return JsonResponse({

                'success': False,

                'message': 'AI Model not trained'

            })

        with open('encodings.pkl', 'rb') as f:

            saved_data = pickle.load(f)

        known_encodings = saved_data['encodings']
        known_names = saved_data['names']

        detected_students = []
        detected_ids = set()

        # =====================================
        # LOOP THROUGH EACH CROPPED FACE
        # =====================================

        for image_data in face_images:

            try:

                format, imgstr = image_data.split(
                    ';base64,'
                )

                image_bytes = base64.b64decode(
                    imgstr
                )

                image = Image.open(

                    io.BytesIO(image_bytes)

                ).convert('RGB')

                rgb_face = np.array(image)

                # =========================
                # FACE ENCODING
                # =========================

                encodings = face_recognition.face_encodings(
                    rgb_face
                )

                if len(encodings) == 0:

                    continue

                face_encoding = encodings[0]

                # =========================
                # FACE DISTANCE
                # =========================

                face_distances = face_recognition.face_distance(

                    known_encodings,

                    face_encoding

                )

                best_match_index = np.argmin(
                    face_distances
                )

                best_distance = face_distances[
                    best_match_index
                ]

                # =========================
                # STRICT ACCURACY
                # =========================

                if best_distance > 0.48:

                    continue

                matches = face_recognition.compare_faces(

                    known_encodings,

                    face_encoding,

                    tolerance=0.42

                )

                if matches[best_match_index]:

                    student_id = known_names[
                        best_match_index
                    ]

                    # PREVENT DUPLICATES

                    if student_id in detected_ids:

                        continue

                    try:

                        student = Student.objects.get(
                            id=student_id
                        )
                        if class_id and str(student.class_name.id) != str(class_id):
                            continue

                    except Student.DoesNotExist:

                        continue

                    # =========================
                    # CHECK FACE DATA EXISTS
                    # =========================

                    has_faces = StudentFace.objects.filter(
                        student=student
                    ).exists()

                    if not has_faces:

                        continue

                    detected_ids.add(student_id)

                    detected_students.append({

                        'id': student.id,

                        'name': student.user.first_name,

                        'register_number':
                        student.register_number,

                        'department':
                        student.department.name,

                        'class_name':
                        student.class_name.name,

                        'subject':
                        subject.name if subject else "No Subject"

                    })

            except Exception as e:

                print(e)

                continue

        return JsonResponse({

            'success': True,

            'students': detected_students

        })

    except Exception as e:

        return JsonResponse({

            'success': False,

            'message': str(e)

        })
@login_required
def finalize_ai_attendance(request):

    if request.method != "POST":
        return JsonResponse({"success": False})

    data = json.loads(request.body)

    teacher = Teacher.objects.filter(
        user=request.user
    ).first()

    if not teacher:
        return JsonResponse({
            "success": False,
            "error": "Teacher access only"
        })

    subject_id = data.get("subject_id")
    class_id = data.get("class_id")
    detected_ids = data.get("detected_ids", [])

    subject = Subject.objects.get(id=subject_id)

    students = Student.objects.filter(
        class_name_id=class_id
    )

    detected_ids = [str(x) for x in detected_ids]

    present_count = 0
    absent_count = 0

    for student in students:

        if str(student.id) in detected_ids:
            status = "Present"
            present_count += 1
        else:
            status = "Absent"
            absent_count += 1

        Attendance.objects.create(
            student=student,
            subject=subject,
            status=status,
            timestamp=timezone.now()
        )

    return JsonResponse({
        "success": True,
        "present_count": present_count,
        "absent_count": absent_count
    })
# =========================
# 🎭 LIVELINESS
# =========================

@login_required
def liveliness(request):

    student = Student.objects.get(
        user=request.user
    )

    # =========================
    # DELETE ONLY CURRENT
    # STUDENT OLD PHOTOS
    # =========================

    old_faces = StudentFace.objects.filter(
        student=student
    )

    for face in old_faces:

        if face.image:

            face.image.delete(
                save=False
            )

    old_faces.delete()

    total_faces = 0

    return render(

        request,

        'student/liveliness.html',

        {

            'student': student,

            'total_faces': total_faces

        }

    )

# =========================
# 🚪 LOGOUT
# =========================

def student_logout(request):

    logout(request)

    return redirect('/')

# =====================================
# 🎓 GROUP ATTENDANCE PAGE
# =====================================

@login_required
def group_attendance(request):

    subjects = Subject.objects.all()

    return render(

        request,

        'teacher/group_attendance.html',

        {

            'subjects': subjects

        }
    )




# =====================================
# 📊 TEACHER REPORTS
# =====================================

@login_required
def teacher_reports(request):

    attendance = Attendance.objects.all().order_by(
        '-timestamp'
    )

    return render(

        request,

        'teacher/teacher_reports.html',

        {

            'attendance': attendance
        }
    )
@login_required
def view_timetable(request):

    student = Student.objects.get(
        user=request.user
    )

    timetables = TimeTable.objects.filter(
        department=student.department,
        class_room=student.class_name
    ).order_by(
        "day",
        "start_time"
    )

    return render(

        request,

        "student/student_timetable.html",

        {
            "timetables": timetables
        }

    )
