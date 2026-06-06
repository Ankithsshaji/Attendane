from django.urls import path
from . import views
from student.views import download_attendance_pdf


urlpatterns = [
    path('teacher-login/', views.teacher_login),
    path('student-login/', views.student_login),
    path('student-dashboard/', views.student_dashboard_api),
    path('student-timetable/', views.student_timetable_api),
    path('student-attendance-history/', views.student_attendance_history_api),
    path('download-attendance-pdf/', download_attendance_pdf),
    path('student-attendance-pdf/',views.student_attendance_pdf_api),
    path('teacher-students-list/',views.teacher_students_list_api),
    path('teacher-subjects/', views.teacher_subjects_api),
    path('teacher-mark-attendance/', views.teacher_mark_attendance_api),
    path('teacher-attendance-report/',views.teacher_attendance_report_api),
    path('teacher-timetable/', views.teacher_timetable_api),
    path('recognize-group/',views.recognize_group_api,),
    path('finalize-ai-attendance/',views.finalize_ai_attendance_api,),
    path('student-save-face/', views.student_save_face_api),
    path('student-train-face/', views.student_train_face_api),
    path(
    'validate-liveliness/',
    views.validate_liveliness,
),

]