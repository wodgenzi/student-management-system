from django import forms
from .models import Enrollment, Student
from datetime import date, timedelta, time
import re
class FlexibleChoiceField(forms.ChoiceField):
    def __init__(self,  *args, check = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.check = check

    def validate(self, value):
        if not self.check(value):
            raise forms.ValidationError('Enter a valid time in HH:MM format.')

class EnrollmentForm(forms.ModelForm):
    FIXED_TIMINGS = [
        ('08:00', '08:00 AM'),
        ('09:00', '09:00 AM'),
        ('14:00', '02:00 PM'),
        ('16:00', '04:00 PM'),
        ('18:00', '06:00 PM'),
    ]
    def __init__(self, *args, update = False, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['timing'] = FlexibleChoiceField(
            choices=[('', 'Select a time')] + self.FIXED_TIMINGS,
            required=True,
            label='Class Timing',
            check = lambda value: bool(re.fullmatch(r'[0-2]\d:[0-5]\d', value))
        )
        if update:
            not_allowed_fields = ['student', 'course']

            self.fields['timing'] = FlexibleChoiceField(
                choices=[(self.instance.timing.strftime('%H:%M'), self.instance.timing.strftime('%I:%M %p'))]  + self.FIXED_TIMINGS,
                required=True,
                label='Class Timing'
            )
            for field_name in list(self.fields):
                if field_name in not_allowed_fields:
                    self.fields.pop(field_name)

    class Meta:
        model = Enrollment
        fields = '__all__'
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'student': 'Student ID',
            'course': 'Course Name',
            'timing': 'Class Timing',
            'start_date': 'Start Date',
            'paid_fee': 'Paid Fee',
            'discount': 'Discount',
            'reference': 'Reference',
            'status': 'Enrollment Status'
        }


class StudentForm(forms.ModelForm):

    class Meta:
        model = Student
        fields = ['name', 'father_name', 'contact']
        labels = {
            'name': 'Full Name',
            'father_name': 'Father Name',
            'contact': 'Contact'
        }