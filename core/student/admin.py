from django.contrib import admin
from django import forms
from django.contrib.auth.models import User

from .models import (
    Department,
    Class,
    Student,
    Subject,
    Attendance
)


class StudentAdminForm(forms.ModelForm):

    full_name = forms.CharField(label="Full Name")

    password = forms.CharField(
        widget=forms.PasswordInput,
        required=False
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        required=False
    )

    class Meta:
        model = Student
        fields = [
            'full_name',
            'register_number',
            'department',
            'class_name',
            'phone',
            'profile_photo'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields['full_name'].initial = self.instance.user.first_name
            self.fields['password'].required = False
            self.fields['confirm_password'].required = False
        else:
            self.fields['password'].required = True
            self.fields['confirm_password'].required = True

        self.fields['class_name'].queryset = Class.objects.none()

        if 'department' in self.data:
            try:
                dept_id = int(self.data.get('department'))
                self.fields['class_name'].queryset = Class.objects.filter(
                    department_id=dept_id
                )
            except:
                pass

        elif self.instance.pk:
            self.fields['class_name'].queryset = Class.objects.filter(
                department=self.instance.department
            )

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        dept = cleaned_data.get('department')
        cls = cleaned_data.get('class_name')

        if password or confirm_password:
            if password != confirm_password:
                raise forms.ValidationError("Passwords do not match")

        if cls and dept and cls.department != dept:
            raise forms.ValidationError(
                "Selected class does not belong to department"
            )

        return cleaned_data


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):

    form = StudentAdminForm

    list_display = (
        'register_number',
        'get_name',
        'department',
        'class_name',
        'phone'
    )

    search_fields = (
        'register_number',
        'user__first_name'
    )

    list_filter = (
        'department',
        'class_name'
    )

    exclude = ('user',)

    class Media:
        js = ('admin/class_filter.js',)

    def get_name(self, obj):
        return obj.user.first_name

    get_name.short_description = "Full Name"

    def save_model(self, request, obj, form, change):

        if not change:
            user = User.objects.create_user(
                username=obj.register_number,
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['full_name']
            )

            obj.user = user

        else:
            user = obj.user
            user.first_name = form.cleaned_data['full_name']

            password = form.cleaned_data.get('password')

            if password:
                user.set_password(password)

            user.save()

        super().save_model(request, obj, form, change)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):

    list_display = (
        'student',
        'subject',
        'timestamp',
        'status',
        'marked_by_ai'
    )

    list_filter = (
        'status',
        'subject',
        'timestamp'
    )

    search_fields = (
        'student__user__first_name',
        'student__register_number'
    )

    ordering = (
        '-timestamp',
    )


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'department',
    )

    search_fields = (
        'name',
        'department__name',
    )

    list_filter = (
        'department',
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):

    list_display = (
        'name',
    )

    search_fields = (
        'name',
    )


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'department'
    )

    list_filter = (
        'department',
    )

    search_fields = (
        'name',
        'department__name',
    )