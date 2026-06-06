import os

from django.db import models

from django.contrib.auth.models import User

from django.utils import timezone


# =====================================
# FACE IMAGE SAVE PATH
# =====================================

def student_face_upload_path(instance, filename):

    full_name = instance.student.user.first_name

    folder_name = (

        full_name
        .strip()
        .lower()
        .replace(" ", "_")
    )

    folder_name += f"_{instance.student.register_number}"

    return os.path.join(

        'student_faces',

        folder_name,

        filename
    )


# =====================================
# DEPARTMENT MODEL
# =====================================

class Department(models.Model):

    name = models.CharField(
        max_length=100
    )

    def __str__(self):

        return self.name


# =====================================
# CLASS MODEL
# =====================================

class Class(models.Model):

    name = models.CharField(
        max_length=100
    )

    department = models.ForeignKey(

        Department,

        on_delete=models.CASCADE
    )

    def __str__(self):

        return self.name


# =====================================
# SUBJECT MODEL
# =====================================

class Subject(models.Model):

    name = models.CharField(
        max_length=100
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE
    )

    def __str__(self):

        return f"{self.name} - {self.department.name}"
# =====================================
# STUDENT MODEL
# =====================================

class Student(models.Model):

    user = models.OneToOneField(

        User,

        on_delete=models.CASCADE
    )

    register_number = models.CharField(

        max_length=50,

        unique=True
    )

    department = models.ForeignKey(

        Department,

        on_delete=models.CASCADE
    )

    class_name = models.ForeignKey(

        Class,

        on_delete=models.CASCADE
    )

    phone = models.CharField(

        max_length=15,

        blank=True,

        null=True
    )

    profile_photo = models.ImageField(

        upload_to='profiles/',

        blank=True,

        null=True
    )

    created_at = models.DateTimeField(

        auto_now_add=True
    )

    def __str__(self):

        return (

            f"{self.user.first_name} "
            f"({self.register_number})"
        )


# =====================================
# STUDENT FACE DATASET
# =====================================

class StudentFace(models.Model):

    student = models.ForeignKey(

        Student,

        on_delete=models.CASCADE,

        related_name='faces'
    )

    image = models.ImageField(

        upload_to=student_face_upload_path
    )

    created_at = models.DateTimeField(

        auto_now_add=True
    )

    def __str__(self):

        return (

            f"{self.student.user.first_name} "
            f"- Face"
        )


# =====================================
# ATTENDANCE MODEL
# =====================================

class Attendance(models.Model):

    STATUS_CHOICES = [

        ('Present', 'Present'),

        ('Absent', 'Absent'),

        ('Late', 'Late'),
    ]

    student = models.ForeignKey(

        Student,

        on_delete=models.CASCADE
    )

    subject = models.ForeignKey(

        Subject,

        on_delete=models.CASCADE,

        null=True,

        blank=True
    )

    timestamp = models.DateTimeField(

        default=timezone.now
    )

    status = models.CharField(

        max_length=10,

        choices=STATUS_CHOICES,

        default='Present'
    )

    marked_by_ai = models.BooleanField(

        default=True
    )

    created_at = models.DateTimeField(

        auto_now_add=True
    )

    def __str__(self):

        subject_name = (

            self.subject.name

            if self.subject

            else "No Subject"
        )

        return (

            f"{self.student.user.first_name} - "
            f"{subject_name} - "
            f"{self.status}"
        )   
    
# =====================================
# ATTENDANCE EVIDENCE MODEL
# =====================================

class AttendanceEvidence(models.Model):

    teacher = models.ForeignKey(
        "teacher.Teacher",
        on_delete=models.CASCADE
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE
    )

    class_room = models.ForeignKey(
        Class,
        on_delete=models.CASCADE
    )

    photo = models.ImageField(
        upload_to="attendance_evidence/"
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.class_room.name} - {self.subject.name}"