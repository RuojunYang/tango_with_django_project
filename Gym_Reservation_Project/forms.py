from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Coach, Court, Report
from django.core.validators import RegexValidator
from datetime import datetime, timedelta


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.type = User.Types.CUSTOMER 
        if commit:
            user.save()
        return user
    
class PaymentForm(forms.Form):
    card_number = forms.CharField(
        max_length=16,
        min_length=13,
        required=True,
        label='Card Number',
        validators=[RegexValidator(r'^\d{13,19}$', 'Enter a valid card number')]
    )
    expiry_date = forms.DateField(
        required=True,
        label='Expiry Date (MM/YY)',
        input_formats=['%m/%y'],
        widget=forms.DateInput(format='%m/%y', attrs={'placeholder': 'MM/YY'})
    )
    cvv = forms.CharField(
        max_length=4,
        min_length=3,
        required=True,
        label='CVV',
        validators=[RegexValidator(r'^\d{3}$', 'Enter a valid CVV')]
    )
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=True,
        label='Amount'
    )

class BookingForm(forms.Form):
    HOURS = [(f"{hour:02d}:00", f"{hour:02d}:00") for hour in range(0, 24)]

    date = forms.DateField(
        label="Select Date",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )

    start_time = forms.ChoiceField(
        choices=HOURS, 
        label="Book start time", 
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    end_time = forms.ChoiceField(
        choices=HOURS, 
        label="Book end time", 
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class ReportForm(forms.ModelForm):
    report_type = forms.ChoiceField(choices=Report.REPORT_TYPES.choices, required=True)
    coach = forms.ModelChoiceField(queryset=Coach.objects.all(), required=False)
    court = forms.ModelChoiceField(queryset=Court.objects.all(), required=False)
    reason = forms.CharField(widget=forms.Textarea, required=True)

    class Meta:
        model = Report
        fields = ["report_type", "coach", "court", "reason"]

    def clean(self):
        cleaned_data = super().clean()
        report_type = cleaned_data.get("report_type")
        coach = cleaned_data.get("coach")
        court = cleaned_data.get("court")

        if report_type == "COACH" and not coach:
            raise forms.ValidationError("Please select a coach.")
        if report_type == "COURT" and not court:
            raise forms.ValidationError("Please select a court.")

        return cleaned_data
    
class CoachSignupForm(UserCreationForm):
    HOURS = [(f"{hour:02d}:00", f"{hour:02d}:00") for hour in range(0, 24)]

    name = forms.CharField(max_length=100, required=True, label="Coach Name")
    work_start_time = forms.ChoiceField(
        choices=HOURS, 
        label="Work Start Time", 
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    work_end_time = forms.ChoiceField(
        choices=HOURS, 
        label="Work End Time", 
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    coach_type = forms.ChoiceField(choices=Coach.COACH_TYPES.choices, required=True, label="Coach Type")
    coach_gender = forms.ChoiceField(choices=Coach.COACH_GENDER.choices, required=True, label="Coach Gender")
    image = forms.ImageField(required=False, label="Coach Photo")
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False,
        label="Coach Description",
        help_text="Enter a description of the coach's background and expertise"
    )

    class Meta:
        model = User
        fields = ["username", "password1", "password2", "name", "work_start_time", "work_end_time", 
                 "coach_type", "coach_gender", "image", "description"]

class CoachUpdateForm(forms.ModelForm):
    class Meta:
        model = Coach
        fields = ['name', 'work_start_time', 'work_end_time', 'image', 'description', 'coach_type', 'coach_gender']
        widgets = {
            'work_start_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'work_end_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})