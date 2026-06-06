import os
import io
import pickle
from PIL import Image
from student.models import StudentFace
import face_recognition
import base64
import numpy as np
import mediapipe as mp
import cv2
from django.core.files.base import ContentFile

from django.http import JsonResponse
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response

from teacher.models import Teacher, TimeTable
from student.models import Student


from student.models import Student, Attendance, Subject
from rest_framework.decorators import api_view
from rest_framework.response import Response
from teacher.models import TimeTable

from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

from django.utils import timezone


@api_view(['POST'])
def teacher_login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)

    if user is None:
        return Response({
            'success': False,
            'message': 'Invalid username or password'
        }, status=400)

    teacher = Teacher.objects.filter(user=user).first()

    if teacher is None:
        return Response({
            'success': False,
            'message': 'Student account not allowed here'
        }, status=403)

    return Response({
        'success': True,
        'username': user.username,
        'name': teacher.name,
        'role': 'teacher'
    })


@api_view(['POST'])
def student_login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)

    if user is None:
        return Response({
            'success': False,
            'message': 'Invalid username or password'
        }, status=400)

    if Teacher.objects.filter(user=user).exists():
        return Response({
            'success': False,
            'message': 'Teacher account not allowed here'
        }, status=403)

    student = Student.objects.filter(user=user).first()

    if student is None:
        return Response({
            'success': False,
            'message': 'Student profile not found'
        }, status=404)

    return Response({
    'success': True,
    'username': user.username,
    'name': user.first_name,
    'register_number': student.register_number,
    'role': 'student'
})


@api_view(['GET'])
def student_dashboard_api(request):
    username = request.GET.get('username')

    student = Student.objects.filter(user__username=username).first()

    if student is None:
        return Response({
            'success': False,
            'message': 'Student not found'
        }, status=404)

    attendance = Attendance.objects.filter(student=student)

    total = attendance.count()
    present = attendance.filter(status='Present').count()
    absent = attendance.filter(status='Absent').count()
    late = attendance.filter(status='Late').count()

    effective_present = present + (late * 0.5)

    percentage = 0
    if total > 0:
        percentage = round((effective_present / total) * 100, 2)

    return Response({
        'success': True,
        'name': student.user.first_name,
        'username': student.user.username,
        'register_number': student.register_number,
        'department': student.department.name,
        'class_name': student.class_name.name,
        'total': total,
        'present': present,
        'absent': absent,
        'late': late,
        'percentage': percentage,
    })


@api_view(['GET'])
def student_timetable_api(request):
    username = request.GET.get('username')

    student = Student.objects.filter(user__username=username).first()

    if student is None:
        return Response({
            'success': False,
            'message': 'Student not found'
        }, status=404)

    timetables = TimeTable.objects.filter(
        department=student.department,
        class_room=student.class_name
    ).order_by('day', 'start_time')

    data = []

    for t in timetables:
        data.append({
            'day': t.day,
            'subject': t.subject.name,
            'teacher': t.teacher.name,
            'department': t.department.name,
            'class_name': t.class_room.name,
            'start_time': t.start_time.strftime('%I:%M %p'),
            'end_time': t.end_time.strftime('%I:%M %p'),
        })

    return Response({
        'success': True,
        'timetable': data
    })

@api_view(['GET'])
def student_attendance_history_api(request):
    username = request.GET.get('username')

    student = Student.objects.filter(
        user__username=username
    ).first()

    if not student:
        return Response({
            'success': False,
            'message': 'Student not found'
        }, status=404)

    attendance = Attendance.objects.filter(
        student=student
    ).select_related('subject').order_by('-timestamp')

    data = []

    for item in attendance:
        data.append({
            'date': item.timestamp.strftime('%d-%m-%Y'),
            'time': item.timestamp.strftime('%I:%M %p'),
            'subject': item.subject.name if item.subject else 'No Subject',
            'status': item.status,
        })

    return Response({
        'success': True,
        'attendance': data
    })

@api_view(['GET'])
def student_attendance_pdf_api(request):
    username = request.GET.get('username')

    student = Student.objects.filter(
        user__username=username
    ).first()

    if not student:
        return Response({
            'success': False,
            'message': 'Student not found'
        }, status=404)

    attendance = Attendance.objects.filter(
        student=student
    ).order_by('-timestamp')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="attendance_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(
        Paragraph(
            f"<b>{student.user.first_name} Attendance Report</b>",
            styles['Title']
        )
    )

    elements.append(Spacer(1, 20))

    data = [['Date', 'Subject', 'Status']]

    for item in attendance:
        data.append([
            item.timestamp.strftime("%d-%m-%Y %I:%M %p"),
            item.subject.name if item.subject else "No Subject",
            item.status,
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

@api_view(['GET'])
def teacher_students_list_api(request):
    students = Student.objects.all().select_related(
        'user',
        'department',
        'class_name'
    ).order_by('department__name', 'class_name__name', 'register_number')

    data = []

    for student in students:
        data.append({
            'id': student.id,
            'name': student.user.first_name,
            'username': student.user.username,
            'register_number': student.register_number,
            'department': student.department.name,
            'class_name': student.class_name.name,
        })

    return Response({
        'success': True,
        'students': data
    })


@api_view(['GET'])
def teacher_subjects_api(request):
    subjects = Subject.objects.all().order_by('name')

    data = []

    for subject in subjects:
        data.append({
            'id': subject.id,
            'name': subject.name,
        })

    return Response({
        'success': True,
        'subjects': data
    })


@api_view(['POST'])
def teacher_mark_attendance_api(request):
    student_id = request.data.get('student_id')
    subject_id = request.data.get('subject_id')
    status = request.data.get('status')

    student = Student.objects.filter(id=student_id).first()
    subject = Subject.objects.filter(id=subject_id).first()

    if not student or not subject:
        return Response({
            'success': False,
            'message': 'Student or subject not found'
        }, status=404)

    Attendance.objects.create(
        student=student,
        subject=subject,
        status=status,
        timestamp=timezone.now()
    )

    return Response({
        'success': True,
        'message': 'Attendance marked successfully'
    })

@api_view(['GET'])
def teacher_attendance_report_api(request):

    attendance = Attendance.objects.all().select_related(
        'student',
        'student__user',
        'subject'
    ).order_by('-timestamp')

    total = attendance.count()
    present = attendance.filter(status='Present').count()
    absent = attendance.filter(status='Absent').count()
    late = attendance.filter(status='Late').count()

    data = []

    for item in attendance:
        data.append({
            'student_name': item.student.user.first_name,
            'register_number': item.student.register_number,
            'subject': item.subject.name if item.subject else 'No Subject',
            'status': item.status,
            'date': item.timestamp.strftime('%d-%m-%Y'),
            'time': item.timestamp.strftime('%I:%M %p'),
        })

    return Response({
        'success': True,
        'total': total,
        'present': present,
        'absent': absent,
        'late': late,
        'attendance': data
    })

@api_view(['GET'])
def teacher_timetable_api(request):
    username = request.GET.get('username')

    teacher = Teacher.objects.filter(
        user__username=username
    ).first()

    if teacher is None:
        return Response({
            'success': False,
            'message': 'Teacher not found'
        }, status=404)

    timetables = TimeTable.objects.filter(
        teacher=teacher
    ).select_related(
        'department',
        'class_room',
        'subject'
    ).order_by(
        'day',
        'start_time'
    )

    data = []

    for item in timetables:
        data.append({
            'id': item.id,
            'day': item.day,
            'subject_id': item.subject.id,
            'class_id': item.class_room.id,
            'subject': item.subject.name,
            'department': item.department.name,
            'class_name': item.class_room.name,
            'start_time': item.start_time.strftime('%I:%M %p'),
            'end_time': item.end_time.strftime('%I:%M %p'),
        })

    return Response({
        'success': True,
        'teacher_name': teacher.name,
        'timetable': data
    })

@api_view(['POST'])
def recognize_group_api(request):
    try:

        image_data = request.data.get('image')
        subject_id = request.data.get('subject_id')

        if not image_data:
            return Response({
                'success': False,
                'message': 'No image received'
            })

        subject = Subject.objects.filter(
            id=subject_id
        ).first()

        format, imgstr = image_data.split(';base64,')
        image_bytes = base64.b64decode(imgstr)

        image = Image.open(
            io.BytesIO(image_bytes)
        ).convert('RGB')

        rgb_frame = np.array(image)

        if not os.path.exists('encodings.pkl'):
            return Response({
                'success': False,
                'message': 'AI model not trained'
            })

        with open('encodings.pkl', 'rb') as f:
            saved_data = pickle.load(f)

        known_encodings = saved_data['encodings']
        known_names = saved_data['names']

        small_frame = cv2.resize(
            rgb_frame,
            (0, 0),
            fx=0.5,
            fy=0.5
        )

        face_locations = face_recognition.face_locations(
            small_frame,
            model='hog'
        )

        face_encodings = face_recognition.face_encodings(
            small_frame,
            face_locations
        )

        detected_students = []

        for face_encoding in face_encodings:

            if len(known_encodings) == 0:
                continue

            face_distances = face_recognition.face_distance(
                known_encodings,
                face_encoding
            )

            best_match_index = np.argmin(face_distances)

            best_distance = face_distances[best_match_index]

            if best_distance > 0.42:
                continue

            matches = face_recognition.compare_faces(
                known_encodings,
                face_encoding,
                tolerance=0.42
            )

            if matches[best_match_index]:

                student_id = known_names[best_match_index]

                student = Student.objects.filter(
                    id=student_id
                ).first()

                if not student:
                    continue

                if any(
                    s['id'] == student.id
                    for s in detected_students
                ):
                    continue

                detected_students.append({
                    'id': student.id,
                    'name': student.user.first_name,
                    'register_number': student.register_number,
                    'department': student.department.name,
                    'class_name': student.class_name.name,
                    'subject': subject.name if subject else 'No Subject'
                })

        return Response({
            'success': True,
            'students': detected_students
        })

    except Exception as e:

        return Response({
            'success': False,
            'message': str(e)
        })


@api_view(['POST'])
def finalize_ai_attendance_api(request):

    try:

        subject_id = request.data.get('subject_id')
        class_id = request.data.get('class_id')
        detected_ids = request.data.get(
            'detected_ids',
            []
        )

        subject = Subject.objects.get(
            id=subject_id
        )

        students = Student.objects.filter(
            class_name_id=class_id
        )

        present_count = 0
        absent_count = 0

        for student in students:

            if student.id in detected_ids:
                status = 'Present'
                present_count += 1
            else:
                status = 'Absent'
                absent_count += 1

            Attendance.objects.create(
                student=student,
                subject=subject,
                status=status,
                timestamp=timezone.now()
            )

        return Response({
            'success': True,
            'present_count': present_count,
            'absent_count': absent_count
        })

    except Exception as e:

        return Response({
            'success': False,
            'message': str(e)
        })

@api_view(['POST'])
def student_save_face_api(request):

    try:

        username = request.data.get('username')
        image_data = request.data.get('image')

        student = Student.objects.filter(
            user__username=username
        ).first()

        if not student:

            return Response({
                'success': False,
                'message': 'Student not found'
            })

        # DELETE OLD FACES ON FIRST NEW CAPTURE

        first_image = request.data.get(
            'first_image',
            False
        )

        if first_image:

            old_faces = StudentFace.objects.filter(
                student=student
            )

            for face in old_faces:

                if face.image:
                    face.image.delete(save=False)

                face.delete()

        image_count = StudentFace.objects.filter(
            student=student
        ).count()

        format, imgstr = image_data.split(';base64,')

        ext = format.split('/')[-1]

        img_data = base64.b64decode(imgstr)

        file_name = f"face_{image_count + 1}.{ext}"

        file = ContentFile(
            img_data,
            name=file_name
        )

        StudentFace.objects.create(
            student=student,
            image=file
        )

        return Response({
            'success': True,
            'message': 'Face saved',
            'total_faces': image_count + 1
        })

    except Exception as e:

        return Response({
            'success': False,
            'message': str(e)
        })


@api_view(['POST'])
def student_train_face_api(request):
    try:
        username = request.data.get('username')

        student = Student.objects.filter(user__username=username).first()

        if not student:
            return Response({
                'success': False,
                'message': 'Student not found'
            })

        faces = StudentFace.objects.filter(
            student=student
        ).order_by('-id')[:30]

        if not faces.exists():
            return Response({
                'success': False,
                'message': 'No face images found'
            })

        known_encodings = []
        known_names = []

        if os.path.exists('encodings.pkl'):
            with open('encodings.pkl', 'rb') as f:
                data = pickle.load(f)
                known_encodings = data['encodings']
                known_names = data['names']

        filtered_encodings = []
        filtered_names = []

        for encoding, name in zip(known_encodings, known_names):
            if str(name) != str(student.id):
                filtered_encodings.append(encoding)
                filtered_names.append(name)

        known_encodings = filtered_encodings
        known_names = filtered_names

        encoded = 0
        skipped = 0

        for face in faces:
            try:
                image_path = face.image.path

                image = face_recognition.load_image_file(image_path)

                locations = face_recognition.face_locations(
                    image,
                    model='hog'
                )

                if len(locations) != 1:
                    skipped += 1
                    continue

                encodings = face_recognition.face_encodings(
                    image,
                    locations,
                    num_jitters=1
                )

                if encodings:
                    known_encodings.append(encodings[0])
                    known_names.append(student.id)
                    encoded += 1
                else:
                    skipped += 1

            except:
                skipped += 1

        with open('encodings.pkl', 'wb') as f:
            pickle.dump({
                'encodings': known_encodings,
                'names': known_names
            }, f)

        return Response({
            'success': True,
            'message': 'Face model trained successfully',
            'encoded': encoded,
            'skipped': skipped
        })

    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        })
    
@api_view(['POST'])
def validate_liveliness(request):

    try:

        image_data = request.data.get("image")
        expected = request.data.get("expected")

        format, imgstr = image_data.split(';base64,')
        img_bytes = base64.b64decode(imgstr)

        np_arr = np.frombuffer(img_bytes, np.uint8)

        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        mp_face_mesh = mp.solutions.face_mesh

        with mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
        ) as face_mesh:

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            results = face_mesh.process(rgb)

            if not results.multi_face_landmarks:

                return Response({
                    "success": False,
                    "message": "No face detected"
                })

            landmarks = results.multi_face_landmarks[0]

            nose = landmarks.landmark[1]

            # FRONT
            if expected == "front":

                return Response({
                    "success": True
                })

            # LEFT
            elif expected == "left":

                if nose.x > 0.52:

                    return Response({
                        "success": True
                    })

            # RIGHT
            elif expected == "right":

                if nose.x < 0.48:

                    return Response({
                        "success": True
                    })

            # UP
            elif expected == "up":

                if nose.y < 0.42:

                    return Response({
                        "success": True
                    })

            # DOWN
            elif expected == "down":

                if nose.y > 0.55:

                    return Response({
                        "success": True
                    })

            # SMILE
            elif expected == "smile":

                left_mouth = landmarks.landmark[61]
                right_mouth = landmarks.landmark[291]

                mouth_width = abs(
                    right_mouth.x - left_mouth.x
                )

                if mouth_width > 0.09:

                    return Response({
                        "success": True
                    })

            # BLINK
            elif expected == "blink":

                left_eye_top = landmarks.landmark[159]
                left_eye_bottom = landmarks.landmark[145]

                eye_height = abs(
                    left_eye_top.y - left_eye_bottom.y
                )

                if eye_height < 0.015:

                    return Response({
                        "success": True
                    })

            return Response({
                "success": False,
                "message": "Movement not detected"
            })

    except Exception as e:

        return Response({
            "success": False,
            "message": str(e)
        })