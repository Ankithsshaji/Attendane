from django.urls import path
from . import views

urlpatterns = [

    # 🔐 AUTH

    path(
        '',
        views.student_login,
        name='student_login'
    ),

    path(
        'student-register/',
        views.student_register,
        name='student_register'
    ),

    path(
        'logout/',
        views.student_logout,
        name='logout'
    ),

    # 🔄 AJAX

    path(
        'ajax/load-classes/',
        views.load_classes,
        name='ajax_load_classes'
    ),

    # 📊 STUDENT MODULES

    path(
        'dashboard/',
        views.student_dashboard,
        name='dashboard'
    ),

    path(
        'profile/',
        views.student_profile,
        name='student_profile'
    ),

    path(
        'attendance/',
        views.student_attendance,
        name='attendance'
    ),

    path(
        'settings/',
        views.student_settings,
        name='settings'
    ),

    path(
        'settings/password/',
        views.change_password,
        name='change_password'
    ),

    # ✅ STUDENT REPORTS

    path(
        'student-reports/',
        views.student_reports,
        name='student_reports'
    ),

    # 🎥 LIVENESS

    path(
        'liveliness/',
        views.liveliness,
        name='liveliness'
    ),

    path(
    'save-face/',
    views.save_face,
    name='save_face'
    ),

    path(
    'finalize-training/',
    views.finalize_training,
    name='finalize_training'
    ),
    # 🤖 AI GROUP ATTENDANCE

    path(
        'group-attendance/',
        views.group_attendance,
        name='group_attendance'
    ),

    path(
        'recognize-group/',
        views.recognize_group,
        name='recognize_group'
    ),

    path("finalize-ai-attendance/", views.finalize_ai_attendance, name="finalize_ai_attendance"),

    path(
    'timetable/',
    views.view_timetable,
    name='timetable'
    ),

    path(
        'download-attendance-pdf/',
        views.download_attendance_pdf,
        name='download_attendance_pdf'
    ),
    path(
    'detect-faces/',
    views.detect_faces
    ),

]