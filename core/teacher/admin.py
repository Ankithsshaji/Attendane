from django.contrib import admin
from django.contrib.auth.models import User
from django import forms

from student.models import Class, Subject
from .models import Teacher, TimeTable


class TeacherAdminForm(forms.ModelForm):

    username = forms.CharField(required=False)

    password = forms.CharField(
        widget=forms.PasswordInput,
        required=False
    )

    class Meta:
        model = Teacher
        fields = [
            'name',
            'departments',
            'classes',
            'subjects',
            'phone',
            'profile_photo'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        department_ids = []

        if self.data:
            department_ids = self.data.getlist('departments')

        elif self.instance.pk:
            department_ids = self.instance.departments.values_list(
                'id',
                flat=True
            )

        if department_ids:
            self.fields['classes'].queryset = Class.objects.filter(
                department_id__in=department_ids
            )

            self.fields['subjects'].queryset = Subject.objects.filter(
                department_id__in=department_ids
            )

        else:
            self.fields['classes'].queryset = Class.objects.none()
            self.fields['subjects'].queryset = Subject.objects.none()

    def clean(self):
        cleaned_data = super().clean()

        departments = cleaned_data.get('departments')
        classes = cleaned_data.get('classes')
        subjects = cleaned_data.get('subjects')

        if departments and classes:
            for cls in classes:
                if cls.department not in departments:
                    raise forms.ValidationError(
                        f"{cls.name} does not belong to selected department."
                    )

        if departments and subjects:
            for subject in subjects:
                if subject.department not in departments:
                    raise forms.ValidationError(
                        f"{subject.name} does not belong to selected department."
                    )

        return cleaned_data

    def save(self, commit=True):
        teacher = super().save(commit=False)

        if not teacher.pk:
            user = User.objects.create_user(
                username=self.cleaned_data['username'],
                password=self.cleaned_data['password']
            )
            teacher.user = user

        if commit:
            teacher.save()
            self.save_m2m()

        return teacher


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):

    form = TeacherAdminForm

    list_display = (
        'name',
        'phone',
    )

    search_fields = (
        'name',
        'phone',
    )

    autocomplete_fields = (
    'departments',
    'classes',
    'subjects',
    )

    class Media:
        js = (
            'teacher/js/teacher_admin.js',
        )

@admin.register(TimeTable)
class TimeTableAdmin(admin.ModelAdmin):

    list_display = (
        'day',
        'start_time',
        'end_time',
        'department',
        'class_room',
        'subject',
        'teacher',
    )

    list_filter = (
        'day',
        'department',
        'class_room',
        'subject',
        'teacher',
    )

    search_fields = (
        'subject__name',
        'teacher__name',
        'class_room__name',
        'department__name',
    )
    class Media:
        js = (
            'teacher/js/timetable_admin.js',
        )