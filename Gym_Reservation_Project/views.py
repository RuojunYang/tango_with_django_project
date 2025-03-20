from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import *
from django.utils.dateparse import parse_datetime
from .models import *
from .forms import *
import json

# Create your views here.

# static path
static_path = './Gym_Reservation_Project/static/Gym_Reservation_Project/'

def home(request):
    return render(request, "home.html")

def select_login(request):
    return render(request, "select_login.html")

def login_customer(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()

            if user.type == User.Types.CUSTOMER:
                login(request, user)
                try:
                    user = User.objects.get(username=request.user.username)
                    customer = Customer.objects.get(user=user)
                except Customer.DoesNotExist:
                    messages.error(request, 'You are not Customer')
                    return redirect('home')

                return redirect("after_login_customer_my_profile")
            else:
                messages.error(request, "Not authorized to log in as a Customer.")
        else:
            form.errors.clear()
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, "login_customer.html", {"form": form})

def login_coach(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.type == User.Types.COACH:
                login(request, user)
                return redirect("after_login_operator")
            else:
                messages.error(request, "Not authorized to log in as a Coach.")
        else:
             form.errors.clear()
             messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, "login_operator.html", {"form": form})

def login_manager(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.type == User.Types.MANAGER:
                login(request, user)
                return redirect("after_login_manager")
            else:
                messages.error(request, "Not authorized to log in as a Manager.")
        else:
             form.errors.clear()
             messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, "login_manager.html", {"form": form})

def signup_func(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()

            Customer.objects.create(
                user=user, 
            )
            form.errors.clear()

            messages.success(request, "Account create successfully")
            return redirect("select_login")
        else:
            messages.error(request, 'Invalid information')
    else:
        form = SignupForm()
    return render(request, "signup.html", {"form": form})

def logout_func(request):
    if request.method == "POST":
        logout(request)
        return redirect("home")

@login_required
def after_login_customer(request):
    try:
        user = User.objects.get(username=request.user.username)
        customer = Customer.objects.get(user=user)
    except Customer.DoesNotExist:
        messages.error(request, 'You are not Customer')
        return redirect('home')
    
    active_coach_count = Appointment_Coach.objects.filter(
        user=user, 
        status=Appointment_Coach.APPOINTMENT_TYPES.SCHEDULED
    ).count()
    
    active_court_count = Appointment_Court.objects.filter(
        user=user, 
        status=Appointment_Court.APPOINTMENT_TYPES.SCHEDULED
    ).count()
    
    total_reviews = Coach_Review.objects.filter(user=user).count() + Court_Review.objects.filter(user=user).count()
    
    reports_count = Report.objects.filter(user=user).count()
    
    context = {
        'customer': customer,
        'active_coach_count': active_coach_count,
        'active_court_count': active_court_count,
        'total_reviews': total_reviews,
        'reports_count': reports_count
    }
    
    return render(request, "after_login_customer.html", context)
    
@login_required
def after_login_customer_coach_list(request):
    try:
        user = User.objects.get(username=request.user.username)
        customer = Customer.objects.get(user=user)
    except Customer.DoesNotExist:
        messages.error(request, 'You are not Customer')
        return redirect('home')
    coaches = Coach.objects.all()
    return render(request, "after_login_customer_coach_list.html", {"coaches": coaches})

@login_required
def after_login_customer_book_coach(request, coach_id):
    try:
        user = User.objects.get(username=request.user.username)
        customer = Customer.objects.get(user=user)
    except Customer.DoesNotExist:
        messages.error(request, 'You are not Customer')
        return redirect('home')
    try:
        coach = Coach.objects.get(id=coach_id)
    except Coach.DoesNotExist:
        messages.error(request, 'Invalid coach ID')
        return redirect('after_login_customer_coach_list')
    
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():

            selected_date = form.cleaned_data["date"]
            start_time_str = form.cleaned_data["start_time"]
            end_time_str = form.cleaned_data["end_time"]

            start_datetime = datetime.combine(selected_date, datetime.strptime(start_time_str, "%H:%M").time())
            end_datetime = datetime.combine(selected_date, datetime.strptime(end_time_str, "%H:%M").time())
            now = datetime.now()

            if start_datetime < now:
                messages.error(request, "You cannot book a time in the past.")
                return redirect("after_login_customer_book_coach", coach_id=coach_id)

            if start_datetime >= end_datetime:
                messages.error(request, "Start time must be before end time.")
                return redirect("after_login_customer_book_coach", coach_id=coach_id)

            if not start_time_str.endswith(":00") or not end_time_str.endswith(":00"):
                messages.error(request, "Not a valid time.")
                return redirect("after_login_customer_book_coach", coach_id=coach_id)

            if datetime.strptime(start_time_str, "%H:%M").time() < coach.work_start_time or datetime.strptime(end_time_str, "%H:%M").time() > coach.work_end_time:
                messages.error(request, "Coach is not available at this time.")
                return redirect("after_login_customer_book_coach", coach_id=coach_id)

            existing_appointment = Appointment_Coach.objects.filter(
                coach=coach,
                appointment_start_time__lt=end_datetime,
                appointment_end_time__gt=start_datetime
            ).exclude(status=Appointment_Coach.APPOINTMENT_TYPES.CANCELED).exists()

            if existing_appointment:
                messages.error(request, "This timeslot has already been booked")
                return redirect("after_login_customer_book_coach", id=coach_id)

            Appointment_Coach.objects.create(
                user=request.user,
                coach=coach,
                appointment_start_time=start_datetime,
                appointment_end_time=end_datetime,
                status=Appointment_Coach.APPOINTMENT_TYPES.SCHEDULED
            )

            messages.success(request, "Booked success")
            return redirect("after_login_customer_my_profile_coach_reservation_scheduled")

    else:
        form = BookingForm()

    return render(request, "after_login_customer_book_coach.html", {"coach": coach, "form": form})

@login_required
def after_login_customer_court_list(request):
    try:
        user = User.objects.get(username=request.user.username)
        customer = Customer.objects.get(user=user)
    except Customer.DoesNotExist:
        messages.error(request, 'You are not Customer')
        return redirect('home')
    courts = Court.objects.all()
    for court in courts:
        print(f"Court ID: {court.id}")
    return render(request, "after_login_customer_court_list.html", {"courts": courts})

@login_required
def after_login_customer_book_court(request, court_id):
    try:
        user = User.objects.get(username=request.user.username)
        customer = Customer.objects.get(user=user)
    except Customer.DoesNotExist:
        messages.error(request, 'You are not Customer')
        return redirect('home')
    try:
        court = Court.objects.get(id=court_id)
    except Court.DoesNotExist:
        messages.error(request, 'Invalid court ID')
        return redirect('after_login_customer_court_list')
    
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():

            selected_date = form.cleaned_data["date"]
            start_time_str = form.cleaned_data["start_time"]
            end_time_str = form.cleaned_data["end_time"]

            start_datetime = datetime.combine(selected_date, datetime.strptime(start_time_str, "%H:%M").time())
            end_datetime = datetime.combine(selected_date, datetime.strptime(end_time_str, "%H:%M").time())
            now = datetime.now()
            
            if start_datetime < now:
                messages.error(request, "You cannot book a time in the past.")
                return redirect("after_login_customer_book_court", court_id=court.id)

            if start_datetime >= end_datetime:
                messages.error(request, "Start time must be before end time.")
                return redirect("after_login_customer_book_court", court_id=court.id)

            if not start_time_str.endswith(":00") or not end_time_str.endswith(":00"):
                messages.error(request, "Not a valid time.")
                return redirect("after_login_customer_book_court", court_id=court.id)
            
            if datetime.strptime(start_time_str, "%H:%M").time() < court.work_start_time or datetime.strptime(end_time_str, "%H:%M").time() > court.work_end_time:
                messages.error(request, "Court is not available at this time.")
                return redirect("after_login_customer_book_court", court_id=court.id)

            existing_appointment = Appointment_Court.objects.filter(
                court=court,
                appointment_start_time__lt=end_datetime,
                appointment_end_time__gt=start_datetime
            ).exclude(status=Appointment_Court.APPOINTMENT_TYPES.CANCELED).exists()

            if existing_appointment:
                messages.error(request, "This timeslot has already been booked")
                return redirect("after_login_customer_book_court", court_id=court.id)

            Appointment_Court.objects.create(
                user=request.user,
                court=court,
                appointment_start_time=start_datetime,
                appointment_end_time=end_datetime,
                status=Appointment_Court.APPOINTMENT_TYPES.SCHEDULED
            )

            messages.success(request, "Booked success")
            return redirect("after_login_customer_my_profile_court_reservation_scheduled")

    else:
        form = BookingForm()

    return render(request, "after_login_customer_book_court.html", {"court": court, "form": form})

@login_required
def after_login_customer_coach_review_list(request, coach_id):
    try:
        user = User.objects.get(username=request.user.username)
        customer = Customer.objects.get(user=user)
    except Customer.DoesNotExist:
        messages.error(request, 'You are not Customer')
        return redirect('home')
    try:
        coach = Coach.objects.get(id=coach_id)
    except:
        messages.error(request, 'Invalid coach ID')
        return redirect('after_login_customer_coach_list')
    
    reviews = Coach_Review.objects.filter(coach=coach).order_by('-created_at')
    return render(request, "after_login_customer_coach_review_list.html", {"reviews": reviews, "coach": coach, "coach_id": coach_id})

@login_required
def after_login_customer_coach_review_write(request, coach_id):
    try:
        user = User.objects.get(username=request.user.username)
        customer = Customer.objects.get(user=user)
    except Customer.DoesNotExist:
        messages.error(request, 'You are not Customer')
        return redirect('home')
    try:
        coach = Coach.objects.get(id=coach_id)
    except Coach.DoesNotExist:
        messages.error(request, 'Invalid coach ID')
        return redirect('after_login_customer_coach_list')

    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            Coach_Review.objects.create(coach=coach, user=request.user, content=content)
            messages.success(request, "Submit success")
            return redirect('after_login_customer_coach_review_list', coach_id=coach_id)
        messages.error(request, "Review cannot be empty")

    return render(request, "after_login_customer_coach_review_write.html", {"coach": coach})

@login_required
def after_login_customer_court_review_list(request, court_id):
    try:
        user = User.objects.get(username=request.user.username)
        customer = Customer.objects.get(user=user)
    except Customer.DoesNotExist:
        messages.error(request, 'You are not Customer')
        return redirect('home')
    try:
        court = Court.objects.get(id=court_id)
    except:
        messages.error(request, 'Invalid court ID')
        return redirect('after_login_customer_court_list')
    
    reviews = Court_Review.objects.filter(court=court).order_by('-created_at')
    return render(request, "after_login_customer_court_review_list.html", {"reviews": reviews, "court": court, "court_id": court_id})


@login_required
def after_login_customer_court_review_write(request, court_id):
    try:
        user = User.objects.get(username=request.user.username)
        customer = Customer.objects.get(user=user)
    except Customer.DoesNotExist:
        messages.error(request, 'You are not Customer')
        return redirect('home')
    try:
        court = Court.objects.get(id=court_id)
    except Court.DoesNotExist:
        messages.error(request, 'Invalid court ID')
        return redirect('after_login_customer_court_list')

    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            Court_Review.objects.create(court=court, user=request.user, content=content)
            messages.success(request, "Submit success")
            return redirect('after_login_customer_court_review_list', court_id=court.id)
        messages.error(request, "Review cannot be empty")

    return render(request, "after_login_customer_court_review_write.html", {"court": court})

@login_required
def after_login_customer_my_profile(request):
    try:
        user = User.objects.get(username=request.user.username)
        customer = Customer.objects.get(user=user)
    except Customer.DoesNotExist:
        messages.error(request, 'You are not Customer')
        return redirect('home')
        
    active_coach_reservations = Appointment_Coach.objects.filter(
        user=user,
        status=Appointment_Coach.APPOINTMENT_TYPES.SCHEDULED
    ).order_by('appointment_start_time')
    
    active_court_reservations = Appointment_Court.objects.filter(
        user=user,
        status=Appointment_Court.APPOINTMENT_TYPES.SCHEDULED
    ).order_by('appointment_start_time')
    
    coach_reviews = Coach_Review.objects.filter(user=user).count()
    court_reviews = Court_Review.objects.filter(user=user).count()
    total_reviews = coach_reviews + court_reviews
    
    reports = Report.objects.filter(user=user)
    reports_count = reports.count()
    
    latest_report = reports.order_by('-created_at').first()
    
    latest_coach_review = Coach_Review.objects.filter(user=user).order_by('-created_at').first()
    latest_court_review = Court_Review.objects.filter(user=user).order_by('-created_at').first()
    
    latest_review = None
    if latest_coach_review and latest_court_review:
        latest_review = latest_coach_review if latest_coach_review.created_at > latest_court_review.created_at else latest_court_review
    elif latest_coach_review:
        latest_review = latest_coach_review
    elif latest_court_review:
        latest_review = latest_court_review
    
    next_coach_reservation = active_coach_reservations.first()
    next_court_reservation = active_court_reservations.first()
    
    context = {
        'customer': customer,
        'active_coach_count': active_coach_reservations.count(),
        'active_court_count': active_court_reservations.count(),
        'next_coach_reservation': next_coach_reservation,
        'next_court_reservation': next_court_reservation,
        'total_reviews': total_reviews,
        'reports_count': reports_count,
        'latest_report': latest_report,
        'latest_review': latest_review,
    }
    
    return render(request, "after_login_customer_my_profile.html", context)

@login_required
def after_login_customer_pay(request):
    try:
        user = User.objects.get(username=request.user.username)
        customer = Customer.objects.get(user=user)
    except Customer.DoesNotExist:
        messages.error(request, 'You are not Customer')
        return redirect('home')
    user_charge = User.objects.get(username=request.user.username)
    customer_charge = Customer.objects.get(user=user_charge)
    if request.method == "POST":
        form = PaymentForm(request.POST)
        try:
            if form.is_valid():
                payment_amount = form.cleaned_data['amount']
                try:
                    user = User.objects.get(username=request.user.username)
                    customer = Customer.objects.get(user=user)
                except Customer.DoesNotExist:
                    messages.error(request, 'You are not Customer')
                    return redirect('home')
                
                if payment_amount <= 0:
                    messages.error(request, 'The payment amount must be greater than 0.')
                else:
                    customer.charge += payment_amount
                    customer.save()
                    messages.success(request, "Payment successfully")
                    return redirect("after_login_customer")
        except:
            messages.error(request, "Payment invalid.")
    else:
        form = PaymentForm()

    return render(request, 'after_login_customer_pay.html', {'form': form,'customer': customer_charge})

@login_required
def after_login_customer_my_profile_coach_reservation_scheduled(request):
    try:
        user = User.objects.get(username=request.user.username)
        customer = Customer.objects.get(user=user)
    except Customer.DoesNotExist:
        messages.error(request, 'You are not Customer')
        return redirect('home')
    reservations = Appointment_Coach.objects.filter(user=request.user, 
                                                    status=Appointment_Coach.APPOINTMENT_TYPES.SCHEDULED, 
                                                    ).order_by('-appointment_start_time')
    return render(request, "after_login_customer_my_profile_coach_reservation_scheduled.html", {"reservations": reservations})


@login_required
def after_login_customer_my_profile_court_reservation_scheduled(request):
    try:
        user = User.objects.get(username=request.user.username)
        customer = Customer.objects.get(user=user)
    except Customer.DoesNotExist:
        messages.error(request, 'You are not Customer')
        return redirect('home')
    reservations = Appointment_Court.objects.filter(user=request.user, 
                                                    status=Appointment_Coach.APPOINTMENT_TYPES.SCHEDULED, 
                                                    ).order_by('-appointment_start_time')
    return render(request, "after_login_customer_my_profile_court_reservation_scheduled.html", {"reservations": reservations})

@login_required
def after_login_customer_my_profile_coach_reservation_all(request):
    try:
        user = User.objects.get(username=request.user.username)
        customer = Customer.objects.get(user=user)
    except Customer.DoesNotExist:
        messages.error(request, 'You are not Customer')
        return redirect('home')
    reservations = Appointment_Coach.objects.filter(user=request.user,).order_by('-appointment_start_time')
    return render(request, "after_login_customer_my_profile_coach_reservation_all.html", {"reservations": reservations})


@login_required
def after_login_customer_my_profile_court_reservation_all(request):
    try:
        user = User.objects.get(username=request.user.username)
        customer = Customer.objects.get(user=user)
    except Customer.DoesNotExist:
        messages.error(request, 'You are not Customer')
        return redirect('home')
    reservations = Appointment_Court.objects.filter(user=request.user,).order_by('-appointment_start_time')
    return render(request, "after_login_customer_my_profile_court_reservation_all.html", {"reservations": reservations})

@login_required
def after_login_customer_my_profile_reviews(request):
    try:
        user = User.objects.get(username=request.user.username)
        customer = Customer.objects.get(user=user)
    except Customer.DoesNotExist:
        messages.error(request, 'You are not Customer')
        return redirect('home')
    coach_reviews = Coach_Review.objects.filter(user=request.user,).order_by('-created_at')
    court_reviews = Court_Review.objects.filter(user=request.user,).order_by('-created_at')
    print(coach_reviews)
    print(court_reviews)
    return render(request, 'after_login_customer_my_profile_reviews.html', {
        'coach_reviews': coach_reviews,
        'court_reviews': court_reviews
    })

@login_required
def cancel_coach_reservation(request, reservation_id):
    try:
        user = User.objects.get(username=request.user.username)
        customer = Customer.objects.get(user=user)
    except Customer.DoesNotExist:
        messages.error(request, 'You are not Customer')
        return redirect('home')
    try:
        reservation = Appointment_Coach.objects.get(id=reservation_id)
    except Appointment_Coach.DoesNotExist:
        messages.error(request, 'Invalid reservation')
        return redirect('after_login_customer_my_profile_coach_reservation_scheduled')
    
    if reservation.status != Appointment_Coach.APPOINTMENT_TYPES.CANCELED:
        reservation.status = Appointment_Coach.APPOINTMENT_TYPES.CANCELED
        reservation.save()
        messages.success(request, "Coach reservation canceled successfully.")
    else:
        messages.warning(request, "This reservation is already canceled.")

    return redirect('after_login_customer_my_profile_coach_reservation_scheduled')

@login_required
def cancel_court_reservation(request, reservation_id):
    try:
        user = User.objects.get(username=request.user.username)
        customer = Customer.objects.get(user=user)
    except Customer.DoesNotExist:
        messages.error(request, 'You are not Customer')
        return redirect('home')
    try:
        reservation = Appointment_Court.objects.get(id=reservation_id)
    except Appointment_Court.DoesNotExist:
        messages.error(request, 'Invalid reservation')
        return redirect('after_login_customer_my_profile_court_reservation_scheduled')
    
    if reservation.status != Appointment_Court.APPOINTMENT_TYPES.CANCELED:
        reservation.status = Appointment_Court.APPOINTMENT_TYPES.CANCELED
        reservation.save()
        messages.success(request, "Coach reservation canceled successfully.")
    else:
        messages.warning(request, "This reservation is already canceled.")

    return redirect('after_login_customer_my_profile_court_reservation_scheduled')

@login_required
def after_login_customer_my_report_list(request):
    reports = Report.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "after_login_customer_my_report_list.html", {"reports": reports})

@login_required
def after_login_customer_report(request):
    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            report_type = form.cleaned_data["report_type"]
            reason = form.cleaned_data["reason"]
            if report_type == "COACH":
                coach = form.cleaned_data["coach"]
                court = None
            elif report_type == "COURT":
                court = form.cleaned_data["court"]
                coach = None
            else:
                messages.error(request, "Invalid report type")
                return redirect("after_login_customer_report")

            Report.objects.create(
                report_id=uuid.uuid4(),
                report_type=report_type,
                coach=coach,
                court=court,
                user=request.user,
                reason=reason,
                status=Report.REPORT_STATUS.PENDING
            )

            messages.success(request, "Report submitted successfully.")
            return redirect("after_login_customer_my_report_list")
        else:
            messages.error(request, "Invalid information")
    else:
        form = ReportForm()

    return render(request, "after_login_customer_report.html", {"form": form})

def login_operator(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.type == User.Types.COACH:
                login(request, user)
                return redirect("after_login_operator")
            else:
                messages.error(request, "Not authorized to log in as a Operator.")
        else:
            form.errors.clear()
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, "login_operator.html", {"form": form})

@login_required
def after_login_operator(request):
    try:
        user = User.objects.get(username=request.user.username)
        operator = Operator.objects.get(user=user)
    except Operator.DoesNotExist:
        messages.error(request, 'You are not Operator')
        return redirect('home')
    return render(request, "after_login_operator.html", )

@login_required
def after_login_operator_my_reservations(request):
    try:
        user = User.objects.get(username=request.user.username)
        operator = Operator.objects.get(user=user)
    except Operator.DoesNotExist:
        messages.error(request, 'You are not Operator')
        return redirect('home')
    coach = Coach.objects.filter(operator=operator)
    
    reservations = Appointment_Coach.objects.filter(status=Appointment_Coach.APPOINTMENT_TYPES.SCHEDULED, coach__in=coach).order_by("-appointment_start_time")
 
    if request.method == "POST":
        appointment_id = request.POST.get("appointment_id")
        new_status = request.POST.get("status")

        if not appointment_id or not new_status:
            messages.error(request, "Invalid request.")
            return redirect("after_login_operator_my_reservations")
        
        try:
            appointment = Appointment_Coach.objects.get(appointment_id=appointment_id)
            if new_status in [Appointment_Coach.APPOINTMENT_TYPES.COMPLETED, Appointment_Coach.APPOINTMENT_TYPES.CANCELED]:
                appointment.status = new_status
                appointment.save()
                messages.success(request, f"Appointment status updated to {new_status}.")
            else:
                messages.error(request, "Invalid status selection.")
        except Appointment_Coach.DoesNotExist:
            messages.error(request, "Appointment not found.")

        return redirect("after_login_operator_my_reservations")

    return render(request, "after_login_operator_my_reservations.html", {"reservations": reservations})

@login_required
def after_login_operator_my_reservations_all(request):
    try:
        user = User.objects.get(username=request.user.username)
        operator = Operator.objects.get(user=user)
    except Operator.DoesNotExist:
        messages.error(request, 'You are not Operator')
        return redirect('home')
    coach = Coach.objects.filter(operator=operator)
    
    reservations = Appointment_Coach.objects.filter(coach__in=coach).order_by("-appointment_start_time")

    return render(request, "after_login_operator_my_reservations_all.html", {"reservations": reservations})

@login_required
def after_login_operator_my_reports(request):
    try:
        user = User.objects.get(username=request.user.username)
        operator = Operator.objects.get(user=user)
    except Operator.DoesNotExist:
        messages.error(request, 'You are not Operator')
        return redirect('home')

    coache = Coach.objects.filter(operator=operator)
    reports = Report.objects.filter(coach__in=coache).order_by("-created_at")

    return render(request, "after_login_operator_my_reports.html", {"reports": reports})

@login_required
def after_login_operator_my_reviews(request):
    try:
        user = User.objects.get(username=request.user.username)
        operator = Operator.objects.get(user=user)
    except Operator.DoesNotExist:
        messages.error(request, 'You are not Operator')
        return redirect('home')

    coache = Coach.objects.filter(operator=operator)
    coach_reviews = Coach_Review.objects.filter(coach__in=coache).select_related('coach', 'user').order_by('-created_at')

    return render(request, 'after_login_manage_review_list.html', {
        'coach_reviews': coach_reviews,
    })

@login_required
def after_login_manager(request):
    try:
        user = User.objects.get(username=request.user.username)
        manager = Manager.objects.get(user=user)
    except Manager.DoesNotExist:
        messages.error(request, 'You are not Manager')
        return redirect('home')

    active_coach_reservations = Appointment_Coach.objects.filter(
        status=Appointment_Coach.APPOINTMENT_TYPES.SCHEDULED
    ).count()
    
    active_court_reservations = Appointment_Court.objects.filter(
        status=Appointment_Court.APPOINTMENT_TYPES.SCHEDULED
    ).count()
    
    coach_count = Coach.objects.count()
    
    customer_count = Customer.objects.count()
    
    pending_reports = Report.objects.filter(
        status=Report.REPORT_STATUS.PENDING
    ).count()
    
    from django.db.models import Count
    from django.db.models.functions import TruncDate
    import datetime
    
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=7)
    
    coach_reservations_by_day = Appointment_Coach.objects.filter(
        appointment_start_time__range=(start_date, end_date)
    ).annotate(
        date=TruncDate('appointment_start_time')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    court_reservations_by_day = Appointment_Court.objects.filter(
        appointment_start_time__range=(start_date, end_date)
    ).annotate(
        date=TruncDate('appointment_start_time')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    coach_types = Coach.objects.values('coach_type').annotate(count=Count('id'))
    
    chart_data = {
        'dates': [],
        'coach_reservations': [],
        'court_reservations': []
    }
    
    date_range = [(end_date - datetime.timedelta(days=i)).date() for i in range(7, 0, -1)]
    chart_data['dates'] = [d.strftime('%Y-%m-%d') for d in date_range]
    
    coach_counts = [0] * 7
    court_counts = [0] * 7
    
    for res in coach_reservations_by_day:
        date_str = res['date'].strftime('%Y-%m-%d')
        if date_str in chart_data['dates']:
            idx = chart_data['dates'].index(date_str)
            coach_counts[idx] = res['count']
    
    for res in court_reservations_by_day:
        date_str = res['date'].strftime('%Y-%m-%d')
        if date_str in chart_data['dates']:
            idx = chart_data['dates'].index(date_str)
            court_counts[idx] = res['count']
    
    chart_data['coach_reservations'] = coach_counts
    chart_data['court_reservations'] = court_counts
    
    chart_data_json = json.dumps(chart_data)
    
    coach_type_data = {}
    coach_types_choices = dict(Coach.COACH_TYPES.choices)
    
    for ct in coach_types:
        coach_type = ct['coach_type']
        count = ct['count']
        
        if coach_type in coach_types_choices:
            coach_type_display = coach_types_choices[coach_type]
        else:
            coach_type_display = coach_type.replace('_', ' ').title()
        
        coach_type_data[coach_type_display] = count
    
    coach_type_data_json = json.dumps(coach_type_data)
    
    context = {
        'active_coach_reservations': active_coach_reservations,
        'active_court_reservations': active_court_reservations,
        'coach_count': coach_count,
        'customer_count': customer_count,
        'pending_reports': pending_reports,
        'chart_data': chart_data_json,
        'coach_type_data': coach_type_data_json
    }
    
    return render(request, "after_login_manager.html", context)

@login_required
def after_login_manager_signup_operator(request):
    try:
        user = User.objects.get(username=request.user.username)
        manager = Manager.objects.get(user=user)
    except Manager.DoesNotExist:
        messages.error(request, 'You are not Manager')
        return redirect('home')

    if request.method == "POST":
        form = CoachSignupForm(request.POST, request.FILES)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            name = form.cleaned_data['name']
            work_start_time = form.cleaned_data['work_start_time']
            work_end_time = form.cleaned_data['work_end_time']
            coach_type = form.cleaned_data['coach_type']
            coach_gender = form.cleaned_data['coach_gender']

            new_user, created_user = User.objects.get_or_create(
                username=username,
                defaults={
                    'type': User.Types.COACH,
                    'password': make_password(password)
                }
            )

            if not created_user:
                messages.error(request, f"Username '{username}' is already taken")
                return render(request, "after_login_manager_signup_operator.html", {"form": form})

            work_start_time_temp = datetime.strptime(form.cleaned_data['work_start_time'], "%H:%M").time()
            work_end_time_temp = datetime.strptime(form.cleaned_data['work_end_time'], "%H:%M").time()

            if work_start_time_temp >= work_end_time_temp:
                messages.error(request, f"Start time must be earlier than end time")
                return render(request, "after_login_manager_signup_operator.html", {"form": form})

            operator = Operator.objects.create(user=new_user)

            image = None
            if 'image' in request.FILES:
                image = request.FILES['image']
                
            description = form.cleaned_data.get('description', '')

            coach = Coach.objects.create(
                name=name,
                work_start_time=work_start_time,
                work_end_time=work_end_time,
                operator=operator,
                coach_type=coach_type,
                coach_gender=coach_gender,
                image=image,
                description=description
            )

            messages.success(request, f"Coach {coach.name} created successfully")
            return redirect("after_login_manage_coaches")
        else:
            messages.error(request, "Invalid infroamtion")
    else:
        form = CoachSignupForm()

    return render(request, "after_login_manager_signup_operator.html", {"form": form})

@login_required
def after_login_manage_scheduled_reports(request):
    try:
        user = User.objects.get(username=request.user.username)
        manager = Manager.objects.get(user=user)
    except Manager.DoesNotExist:
        messages.error(request, 'You are not Manager')
        return redirect('home')
    reports = Report.objects.filter(status=Report.REPORT_STATUS.PENDING).order_by("-created_at")

    if request.method == "POST":
        report_id = request.POST.get("report_id")
        action = request.POST.get("action")

        try:
            report = Report.objects.get(report_id=report_id)
        except Report.DoesNotExist:
            messages.error(request, 'Invalid report id')
            return redirect('after_login_manage_scheduled_reports')
        
        if action == "resolve":
            report.status = Report.REPORT_STATUS.RESOLVED
        elif action == "reject":
            report.status = Report.REPORT_STATUS.REJECTED

        report.save()
        messages.success(request, "Report updated successfully.")

    return render(request, "after_login_manage_scheduled_reports.html", {"reports": reports})

@login_required
def after_login_manage_all_reports(request):
    try:
        user = User.objects.get(username=request.user.username)
        manager = Manager.objects.get(user=user)
    except Manager.DoesNotExist:
        messages.error(request, 'You are not Manager')
        return redirect('home')
    reports = Report.objects.order_by("-created_at")

    return render(request, "after_login_manage_all_reports.html", {"reports": reports})

@login_required
def after_login_manage_coach_reservations(request):
    try:
        user = User.objects.get(username=request.user.username)
        manager = Manager.objects.get(user=user)
    except Manager.DoesNotExist:
        messages.error(request, 'You are not Manager')
        return redirect('home')

    reservations = Appointment_Coach.objects.all().order_by("-appointment_start_time")

    if request.method == "POST":
        appointment_id = request.POST.get("appointment_id")
        new_status = request.POST.get("status")

        try:
            appointment = Appointment_Coach.objects.get(appointment_id=appointment_id)
            if new_status in [Appointment_Coach.APPOINTMENT_TYPES.COMPLETED, Appointment_Coach.APPOINTMENT_TYPES.CANCELED]:
                appointment.status = new_status
                appointment.save()
                messages.success(request, f"Appointment status updated to {new_status}.")
            else:
                messages.error(request, "Invalid status selection.")
        except Appointment_Coach.DoesNotExist:
            messages.error(request, "Appointment not found.")

        return redirect("after_login_manage_coach_reservations")

    return render(request, "after_login_manage_coach_reservations.html", {"reservations": reservations})

@login_required
def after_login_manage_court_reservations(request):
    try:
        user = User.objects.get(username=request.user.username)
        manager = Manager.objects.get(user=user)
    except Manager.DoesNotExist:
        messages.error(request, 'You are not Manager')
        return redirect('home')

    reservations = Appointment_Court.objects.all().order_by("-appointment_start_time")

    if request.method == "POST":
        appointment_id = request.POST.get("appointment_id")
        new_status = request.POST.get("status")

        try:
            appointment = Appointment_Court.objects.get(appointment_id=appointment_id)
            if new_status in [Appointment_Court.APPOINTMENT_TYPES.COMPLETED, Appointment_Court.APPOINTMENT_TYPES.CANCELED]:
                appointment.status = new_status
                appointment.save()
                messages.success(request, f"Appointment status updated to {new_status}.")
            else:
                messages.error(request, "Invalid status selection.")
        except Appointment_Court.DoesNotExist:
            messages.error(request, "Appointment not found.")

        return redirect("after_login_manage_court_reservations")

    return render(request, "after_login_manage_court_reservations.html", {"reservations": reservations})

@login_required
def after_login_manage_review_list(request):
    try:
        user = User.objects.get(username=request.user.username)
        manager = Manager.objects.get(user=user)
    except Manager.DoesNotExist:
        messages.error(request, 'You are not Manager')
        return redirect('home')

    coach_reviews = Coach_Review.objects.select_related('coach', 'user').order_by('-created_at')
    court_reviews = Court_Review.objects.select_related('court', 'user').order_by('-created_at')

    return render(request, 'after_login_manage_review_list.html', {
        'coach_reviews': coach_reviews,
        'court_reviews': court_reviews
    })

@login_required
def after_login_manage_review_list_coach(request):
    try:
        user = User.objects.get(username=request.user.username)
        manager = Manager.objects.get(user=user)
    except Manager.DoesNotExist:
        messages.error(request, 'You are not Manager')
        return redirect('home')

    coach_reviews = Coach_Review.objects.select_related('coach', 'user').order_by('-created_at')

    return render(request, 'after_login_manage_review_list_coach.html', {
        'coach_reviews': coach_reviews,
    })

@login_required
def after_login_manage_review_list_court(request):
    try:
        user = User.objects.get(username=request.user.username)
        manager = Manager.objects.get(user=user)
    except Manager.DoesNotExist:
        messages.error(request, 'You are not Manager')
        return redirect('home')

    court_reviews = Court_Review.objects.select_related('court', 'user').order_by('-created_at')

    return render(request, 'after_login_manage_review_list_court.html', {
        'court_reviews': court_reviews
    })

@login_required
def after_login_manage_coaches(request):
    try:
        user = User.objects.get(username=request.user.username)
        manager = Manager.objects.get(user=user)
    except Manager.DoesNotExist:
        messages.error(request, 'You are not Manager')
        return redirect('home')
    
    coaches = Coach.objects.all().order_by('id')
    
    return render(request, 'after_login_manage_coaches.html', {
        'coaches': coaches
    })

@login_required
def after_login_manage_coach_edit(request, coach_id):
    try:
        user = User.objects.get(username=request.user.username)
        manager = Manager.objects.get(user=user)
    except Manager.DoesNotExist:
        messages.error(request, 'You are not Manager')
        return redirect('home')
    
    try:
        coach = Coach.objects.get(id=coach_id)
    except Coach.DoesNotExist:
        messages.error(request, 'Coach not found')
        return redirect('after_login_manage_coaches')
    
    if request.method == "POST":
        name = request.POST.get('name')
        coach_type = request.POST.get('coach_type')
        coach_gender = request.POST.get('coach_gender')
        work_start_time = request.POST.get('work_start_time')
        work_end_time = request.POST.get('work_end_time')
        description = request.POST.get('description')
        
        if work_start_time >= work_end_time:
            messages.error(request, 'Work end time must be after work start time')
            return render(request, 'after_login_manage_coach_edit.html', {'coach': coach})
        
        coach.name = name
        coach.coach_type = coach_type
        coach.coach_gender = coach_gender
        coach.work_start_time = work_start_time
        coach.work_end_time = work_end_time
        coach.description = description
        
        if 'image' in request.FILES:
            coach.image = request.FILES['image']
        
        coach.save()
        messages.success(request, 'Coach information updated successfully')
        return redirect('after_login_manage_coaches')
    
    return render(request, 'after_login_manage_coach_edit.html', {
        'coach': coach
    })

@login_required
def after_login_customer_edit_profile(request):
    try:
        user = User.objects.get(username=request.user.username)
        customer = Customer.objects.get(user=user)
    except Customer.DoesNotExist:
        messages.error(request, 'You are not a customer')
        return redirect('home')
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email', '')
        mobile = request.POST.get('mobile', '')
        address = request.POST.get('address', '')
        
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()
        
        customer.mobile = mobile
        customer.address = address
        customer.save()
        
        if 'profile_image' in request.FILES:
            try:
                user.profile_image = request.FILES['profile_image']
                user.save()
            except Exception as e:
                messages.error(request, f'Profile image upload failed: {str(e)}')
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('after_login_customer_my_profile')
    
    return render(request, 'after_login_customer_edit_profile.html', {'customer': customer})

@login_required
def after_login_manage_coach_delete(request, coach_id):
    try:
        user = User.objects.get(username=request.user.username)
        manager = Manager.objects.get(user=user)
    except Manager.DoesNotExist:
        messages.error(request, 'You are not Manager')
        return redirect('home')
    
    try:
        coach = Coach.objects.get(id=coach_id)
        operator = coach.operator
        user = operator.user
        
        Appointment_Coach.objects.filter(coach=coach).delete()
        Coach_Review.objects.filter(coach=coach).delete()
        Report.objects.filter(coach=coach).delete()
        
        coach.delete()
        operator.delete()
        user.delete()
        
        messages.success(request, 'Coach deleted successfully')
    except Coach.DoesNotExist:
        messages.error(request, 'Coach not found')
    except Exception as e:
        messages.error(request, f'Error deleting coach: {str(e)}')
    
    return redirect('after_login_manage_coaches')