from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path('', views.home, name='home'),

    path('select_login/', views.select_login, name="select_login"),
    path('login_customer/', views.login_customer, name="login_customer"),
    path('login_operator/', views.login_operator, name="login_operator"),
    path('login_manager/', views.login_manager, name="login_manager"),

    path('signup/', views.signup_func, name="signup"),
    path('logout/', views.logout_func, name="logout"),

    path('after_login_customer/', views.after_login_customer, name="after_login_customer"),
    path('after_login_operator/', views.after_login_operator, name="after_login_operator"),
    path('after_login_manager/', views.after_login_manager, name="after_login_manager"),

    # customer
    path("after_login_customer/coach_list/", views.after_login_customer_coach_list, name="after_login_customer_coach_list"),
    path("after_login_customer/court_list/", views.after_login_customer_court_list, name="after_login_customer_court_list"),

    path("after_login_customer/coach_list/<int:coach_id>/coach_book/", views.after_login_customer_book_coach, name="after_login_customer_book_coach"),
    path("after_login_customer/court_list/<int:court_id>/court_book/", views.after_login_customer_book_court, name="after_login_customer_book_court"),

    path("after_login_customer/coach_list/<int:coach_id>/coach_review_list/", views.after_login_customer_coach_review_list, name="after_login_customer_coach_review_list"),
    path("after_login_customer/coach_list/<int:coach_id>/coach_review_write/", views.after_login_customer_coach_review_write, name="after_login_customer_coach_review_write"),

    path("after_login_customer/court_list/<int:court_id>/court_review_list/", views.after_login_customer_court_review_list, name="after_login_customer_court_review_list"),
    path("after_login_customer/court_list/<int:court_id>/court_review_write/", views.after_login_customer_court_review_write, name="after_login_customer_court_review_write"),

    path('after_login_customer/my_profile/', views.after_login_customer_my_profile, name="after_login_customer_my_profile"),
    path('after_login_customer/my_profile/edit/', views.after_login_customer_edit_profile, name="after_login_customer_edit_profile"),

    path('after_login_customer/my_profile/coach_reservation/scheduled/', views.after_login_customer_my_profile_coach_reservation_scheduled, name="after_login_customer_my_profile_coach_reservation_scheduled"),
    path('after_login_customer/my_profile/court_reservation/scheduled/', views.after_login_customer_my_profile_court_reservation_scheduled, name="after_login_customer_my_profile_court_reservation_scheduled"),
    path('after_login_customer/my_profile/coach_reservation/all/', views.after_login_customer_my_profile_coach_reservation_all, name="after_login_customer_my_profile_coach_reservation_all"),
    path('after_login_customer/my_profile/court_reservation/all/', views.after_login_customer_my_profile_court_reservation_all, name="after_login_customer_my_profile_court_reservation_all"),
    path('after_login_customer/my_profile/cancel_coach_reservation/<int:reservation_id>/', views.cancel_coach_reservation, name='cancel_coach_reservation'),
    path('after_login_customer/my_profile/cancel_court_reservation/<int:reservation_id>/', views.cancel_court_reservation, name='cancel_court_reservation'),

    path('after_login_customer/my_profile/my_reports/', views.after_login_customer_my_report_list, name='after_login_customer_my_report_list'),
    path('after_login_customer/report/', views.after_login_customer_report, name='after_login_customer_report'),

    path('after_login_customer/my_profile/my_reviews/', views.after_login_customer_my_profile_reviews, name='after_login_customer_my_profile_reviews'),

    # operator
    path('after_login_operator/my_reservations/', views.after_login_operator_my_reservations, name='after_login_operator_my_reservations'),
    path('after_login_operator/my_reservations_all/', views.after_login_operator_my_reservations_all, name='after_login_operator_my_reservations_all'),

    path('after_login_operator/my_reports/', views.after_login_operator_my_reports, name='after_login_operator_my_reports'),
    path('after_login_operator/my_reviews/', views.after_login_operator_my_reviews, name='after_login_operator_my_reviews'),

    # manager
    path('after_login_manager/signup_operator/', views.after_login_manager_signup_operator, name="after_login_manager_signup_operator"),
    
    path('after_login_manager/scheduled_reports/', views.after_login_manage_scheduled_reports, name="after_login_manage_scheduled_reports"),
    path('after_login_manager/all_reports/', views.after_login_manage_all_reports, name="after_login_manage_all_reports"),

    path('after_login_manager/coach_reservations/', views.after_login_manage_coach_reservations, name="after_login_manage_coach_reservations"),
    path('after_login_manager/court_reservations/', views.after_login_manage_court_reservations, name="after_login_manage_court_reservations"),

    path('after_login_manage/review_list/', views.after_login_manage_review_list, name='after_login_manage_review_list'),
    path('after_login_manage/review_list_coach/', views.after_login_manage_review_list_coach, name='after_login_manage_review_list_coach'),
    path('after_login_manage/review_list_court/', views.after_login_manage_review_list_court, name='after_login_manage_review_list_court'),
    
    # Manager coach management
    path('after_login_manage/coaches/', views.after_login_manage_coaches, name='after_login_manage_coaches'),
    path('after_login_manage/coaches/<int:coach_id>/edit/', views.after_login_manage_coach_edit, name='after_login_manage_coach_edit'),
    path('after_login_manage/coaches/<int:coach_id>/delete/', views.after_login_manage_coach_delete, name='after_login_manage_coach_delete'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
