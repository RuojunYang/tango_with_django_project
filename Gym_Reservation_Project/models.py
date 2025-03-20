# python manage.py makemigrations
# python manage.py migrate
# python manage.py createsuperuser
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password
import uuid
# Create your models here.

class User(AbstractUser):
    class Types(models.TextChoices):
        CUSTOMER = "CUSTOMER", "Customer"
        COACH = "COACH", "Coach"
        MANAGER = "MANAGER", "Manager"

    type = models.CharField(
        max_length=50,
        choices=Types.choices,
        default=Types.CUSTOMER
    )
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pk and self.type is None:
            self.type = self.Types.CUSTOMER
        super().save(*args, **kwargs)

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    password = models.CharField(max_length=128)
    is_taking_course = models.BooleanField(default=False)
    is_using_court = models.BooleanField(default=False)
    charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if self.password:
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username

class Operator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    password = models.CharField(max_length=128)

    def save(self, *args, **kwargs):
        if self.password:
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username
    
class Manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    password = models.CharField(max_length=128)

    def save(self, *args, **kwargs):
        if self.password:
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username

class Coach(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    work_start_time = models.TimeField()
    work_end_time = models.TimeField()
    image = models.ImageField(upload_to='coach_images/', blank=True, null=True, default='coach_images/coach1.png')
    description = models.TextField(blank=True, null=True, default="Experienced fitness professional dedicated to helping clients achieve their health and fitness goals.")
    
    operator = models.OneToOneField(Operator, on_delete=models.CASCADE)

    class COACH_TYPES(models.TextChoices):
        FITNESS_TRAINER = 'FITNESS_TRAINER', 'Fitness Trainer'
        GROUP_FITNESS_INSTRUCTOR = 'GROUP_FITNESS_INSTRUCTOR', 'Group Fitness Instructor'
        FUNCTIONAL_TRAINER = 'FUNCTIONAL_TRAINER', 'Functional Trainer'

    coach_type = models.CharField(max_length=50, choices=COACH_TYPES.choices, default=COACH_TYPES.FITNESS_TRAINER)

    class COACH_GENDER(models.TextChoices):
        MALE = 'MALE', 'Male'
        FEMALE = 'FEMALE', 'Female'

    coach_gender = models.CharField(max_length=10, choices=COACH_GENDER.choices, default=COACH_GENDER.MALE)

    def __str__(self):
        return f"Coach {self.id} - {self.coach_gender} - {self.coach_type}"
    
class Court(models.Model):
    id = models.AutoField(primary_key=True)
    balance = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    work_start_time = models.TimeField()
    work_end_time = models.TimeField()

    class COURT_TYPES(models.TextChoices):
        BADMINTON = 'BADMINTON', 'Badminton'
        BASKETBALL = 'BASKETBALL', 'Basketball'

    court_type = models.CharField(max_length=50, choices=COURT_TYPES.choices, default=COURT_TYPES.BADMINTON)

    def __str__(self):
        return f"Court {self.id} - {self.court_type}"
    

class Appointment_Coach(models.Model):
    appointment_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="appointments_coach")
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE, related_name="coach_appointments")

    appointment_start_time = models.DateTimeField()
    appointment_end_time = models.DateTimeField()

    class APPOINTMENT_TYPES(models.TextChoices):
        SCHEDULED = 'SCHEDULED', 'Scheduled'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELED = 'CANCELED', 'Canceled'

    status = models.CharField(max_length=50, choices=APPOINTMENT_TYPES.choices, default=APPOINTMENT_TYPES.SCHEDULED)

    def __str__(self):
        return f"{self.user.username} - {self.coach.name} - start: {self.appointment_start_time} - end: {self.appointment_end_time}"

class Appointment_Court(models.Model):
    appointment_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="appointments_court")
    court = models.ForeignKey(Court, on_delete=models.CASCADE, related_name="appointments_court")
    appointment_start_time = models.DateTimeField()
    appointment_end_time = models.DateTimeField()

    class APPOINTMENT_TYPES(models.TextChoices):
        SCHEDULED = 'SCHEDULED', 'Scheduled'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELED = 'CANCELED', 'Canceled'

    status = models.CharField(max_length=50, choices=APPOINTMENT_TYPES.choices, default=APPOINTMENT_TYPES.SCHEDULED)

    def __str__(self):
        return f"{self.user.username} - {self.court.id} - {self.court.court_type} - start: {self.appointment_start_time} - end: {self.appointment_end_time}"
        
class Report(models.Model):
    class REPORT_STATUS(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        RESOLVED = 'RESOLVED', 'Resolved'
        REJECTED = 'REJECTED', 'Rejected'

    class REPORT_TYPES(models.TextChoices):
        COACH = 'COACH', 'Coach'
        COURT = 'COURT', 'Court'

    report_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    report_type = models.CharField(max_length=10, choices=REPORT_TYPES.choices)
    coach = models.ForeignKey(Coach, null=True, blank=True, on_delete=models.CASCADE, related_name="coach_reports")
    court = models.ForeignKey(Court, null=True, blank=True, on_delete=models.CASCADE, related_name="court_reports")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_reports")
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=REPORT_STATUS.choices, default=REPORT_STATUS.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.report_type == 'COACH':
            return f"{self.report_id}: {self.user.username} - Coach {self.coach.name} - {self.status}"
        elif self.report_type == 'COURT':
            return f"{self.report_id}: {self.user.username} - Court {self.court} - {self.status}"
        return f"{self.report_id}: {self.user.username} - Unknown Report - {self.status}"


class Coach_Review(models.Model):
    review_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE, related_name="coach_reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_reviews")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} on {self.coach.name} on {self.created_at}"

class Court_Review(models.Model):
    review_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    court = models.ForeignKey(Court, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} on {self.court.id} on {self.created_at}"
    