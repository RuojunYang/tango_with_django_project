from django.contrib import admin
from .models import *
from django.core.files import File
# Register your models here.

admin.site.register(Customer)
admin.site.register(Operator)
admin.site.register(Coach)
admin.site.register(Manager)
admin.site.register(Court)
admin.site.register(User)
admin.site.register(Appointment_Court)
admin.site.register(Appointment_Coach)
admin.site.register(Coach_Review)
admin.site.register(Court_Review)

# customer
image = "media/profile_images/default.png"
with open(image, "rb") as img:
    new_user, created_user = User.objects.get_or_create(
        username='customer',
        defaults={
            'type': User.Types.CUSTOMER, 
            'password': make_password('password123'), 
            'profile_image': File(img)
        }
    )

    if created_user:
        operator_instance, created_operator = Customer.objects.get_or_create(
            user=new_user,
            defaults={
                
            }
        )

# operator
new_user, created_user = User.objects.get_or_create(
    username='coach1',
    defaults={
        'type': User.Types.COACH,
        'password': make_password('password123')
    }
)

operator, created_operator = Operator.objects.get_or_create(user=new_user)

if created_operator:
    image = "media/coach_images/coach1.png"
    with open(image, "rb") as img:
        coach = Coach.objects.create(
            name="Coach name 1",
            work_start_time="09:00:00",
            work_end_time="17:00:00",
            operator=operator,
            coach_type=Coach.COACH_TYPES.FITNESS_TRAINER,
            coach_gender=Coach.COACH_GENDER.MALE,
            image=File(img)
        )

new_user, created_user = User.objects.get_or_create(
    username='coach2',
    defaults={
        'type': User.Types.COACH,
        'password': make_password('password123')
    }
)

operator, created_operator = Operator.objects.get_or_create(user=new_user)

if created_operator:
    image = "media/coach_images/coach2.png"
    with open(image, "rb") as img:
        coach = Coach.objects.create(
            name="Coach name 2",
            work_start_time="09:00:00",
            work_end_time="17:00:00",
            operator=operator,
            coach_type=Coach.COACH_TYPES.FUNCTIONAL_TRAINER,
            coach_gender=Coach.COACH_GENDER.FEMALE,
            image=File(img)
        )


# manager
new_user, created_user = User.objects.get_or_create(
    username='manager',
    defaults={
        'type': User.Types.MANAGER, 
        'password': make_password('password123')
    }
)

if created_user:
    operator_instance, created_operator = Manager.objects.get_or_create(
        user=new_user,
        defaults={
        }
    )

new_user, created_user = Court.objects.get_or_create(
    id="001",
    defaults={
        'id': '001',
        'work_start_time': "09:00:00",
        'work_end_time': "17:00:00",
        'court_type': Court.COURT_TYPES.BASKETBALL,
    }
)

new_user, created_user = Court.objects.get_or_create(
    id="002",
    defaults={
        'id': '002',
        'work_start_time': "09:00:00",
        'work_end_time': "17:00:00",
        'court_type': Court.COURT_TYPES.BADMINTON,
    }
)
