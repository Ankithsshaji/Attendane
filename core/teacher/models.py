from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from student.models import (
    Department,
    Class,
    Subject
)


# =========================
# TEACHER MODEL
# =========================

class Teacher(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='teacher'
    )

    name = models.CharField(max_length=100)

    departments = models.ManyToManyField(
        Department,
        blank=True
    )

    classes = models.ManyToManyField(
        Class,
        blank=True
    )

    subjects = models.ManyToManyField(
        Subject,
        blank=True
    )

    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    profile_photo = models.ImageField(
        upload_to='teacher_profiles/',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name


# =========================
# TIMETABLE MODEL
# =========================

class TimeTable(models.Model):

    DAYS = [
        ("Monday", "Monday"),
        ("Tuesday", "Tuesday"),
        ("Wednesday", "Wednesday"),
        ("Thursday", "Thursday"),
        ("Friday", "Friday"),
        ("Saturday", "Saturday"),
    ]

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE
    )

    class_room = models.ForeignKey(
        Class,
        on_delete=models.CASCADE
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE
    )

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE
    )

    day = models.CharField(
        max_length=20,
        choices=DAYS
    )

    start_time = models.TimeField()

    end_time = models.TimeField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = [
            'day',
            'start_time'
        ]

    def clean(self):

        # CLASS MUST BELONG TO SELECTED DEPARTMENT
        if self.class_room and self.department:
            if self.class_room.department != self.department:
                raise ValidationError(
                    "Selected class does not belong to selected department."
                )

        # SUBJECT MUST BELONG TO SELECTED DEPARTMENT
        if self.subject and self.department:
            if self.subject.department != self.department:
                raise ValidationError(
                    "Selected subject does not belong to selected department."
                )

        # SUBJECT MUST BELONG TO SELECTED CLASS
        if self.subject and self.class_room:

            if hasattr(self.subject, 'class_room'):

                if self.subject.class_room != self.class_room:
                    raise ValidationError(
                        "Selected subject does not belong to selected class."
                    )

            elif hasattr(self.subject, 'class_name'):

                if self.subject.class_name != self.class_room:
                    raise ValidationError(
                        "Selected subject does not belong to selected class."
                    )

            elif hasattr(self.subject, 'classes'):

                if self.class_room not in self.subject.classes.all():
                    raise ValidationError(
                        "Selected subject does not belong to selected class."
                    )

        # TEACHER MUST BE ASSIGNED TO THIS DEPARTMENT
        if self.teacher and self.department:
            if self.department not in self.teacher.departments.all():
                raise ValidationError(
                    "Selected teacher is not assigned to this department."
                )

        # TEACHER MUST BE ASSIGNED TO THIS CLASS
        if self.teacher and self.class_room:
            if self.class_room not in self.teacher.classes.all():
                raise ValidationError(
                    "Selected teacher is not assigned to this class."
                )

        # TEACHER MUST BE ASSIGNED TO THIS SUBJECT
        if self.teacher and self.subject:
            if self.subject not in self.teacher.subjects.all():
                raise ValidationError(
                    "Selected teacher is not assigned to this subject."
                )

        # END TIME MUST BE AFTER START TIME
        if self.start_time and self.end_time:
            if self.end_time <= self.start_time:
                raise ValidationError(
                    "End time must be after start time."
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.class_room.name} - {self.subject.name} - {self.day}"