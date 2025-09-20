from django.urls import path
from . import views

urlpatterns = [
    path('', views.admissions, name="admissions"),
    path('enrollments/', views.sc_enrollments, name="sc_enrollments"),
    path('dashboard/', views.sc_dashboard, name='sc_dashboard'),
    path('students/', views.sc_students, name='sc_students'),
    path('update-enrollment/<int:enrollment_id>/', views.update_enrollment, name="update_enrollment"),
    path('update-student/<int:student_id>/', views.update_student, name="update_student"),
    path('add-enrollment/<int:enrollment_id>', views.update_enrollment_form, name='update_enrollment_form'),
    path('add-enrollment/', views.add_enrollment, name="add_enrollment"),
    path('delete-enrollment/<int:enrollment_id>/', views.delete_enrollment, name='delete_enrollment'),
    path('add-student/', views.add_student, name="add_student"),
    path('add-contact/', views.add_contact, name='add_contact'),
    path('get_student/<str:student_id>/', views.get_student, name='get_student'),
    path('upload/', views.upload_file, name='upload_file'),
    path('refresh-cache/', views.refresh_cache, name='refresh-cache'),

]