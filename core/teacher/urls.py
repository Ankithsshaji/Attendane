from django.urls import path
from . import views

urlpatterns = [

    # LOGIN

    path(
        'teacher-login/',
        views.teacher_login,
        name='teacher_login'
    ),

    # DASHBOARD

    path(
        'teacher/dashboard/',
        views.teacher_dashboard,
        name='teacher_dashboard'
    ),

    # MARK ATTENDANCE

    path(
        'teacher/mark-attendance/',
        views.mark_attendance,
        name='teacher_mark_attendance'
    ),

    # ATTENDANCE

    path(
        'teacher/attendance/',
        views.mark_attendance,
        name='teacher_attendance'
    ),

    # REPORTS

    path(
        'teacher/reports/',
        views.teacher_reports,
        name='teacher_reports'
    ),

    # PROFILE

    path(
        'teacher/profile/',
        views.teacher_profile,
        name='teacher_profile'
    ),

    # SETTINGS

    path(
        'teacher/settings/',
        views.teacher_settings,
        name='teacher_settings'
    ),

    path(
        'teacher/change-password/',
        views.change_password,
        name='change_password'
    ),

    # LOGOUT

    path(
        'teacher/logout/',
        views.teacher_logout,
        name='teacher_logout'
    ),
    path(
    'teacher/load-data/',
    views.load_teacher_data,
    name='load_teacher_data'
    ),

    path(
    'teacher/timetable/',
    views.teacher_timetable,
    name='teacher_timetable'
),

    path(
    'teacher/attendance/<int:attendance_id>/edit/',
    views.edit_attendance,
    name='edit_attendance'
),

path(
    "teacher/upload-evidence/",
    views.upload_attendance_evidence,
    name="upload_attendance_evidence"
),

path(
    'teacher/evidence/<int:attendance_id>/',
    views.view_evidence,
    name='view_evidence'
),

]