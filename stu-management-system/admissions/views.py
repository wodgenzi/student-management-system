import json
from services.contacts_cache import contact_exists, add_contact_cache, load_contacts
from services.contacts import get_service, create_contact, get_numbers_in_group
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .forms import EnrollmentForm, StudentForm
from .models import  Enrollment, Course, Student
from accounts.models import Profile
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
import os

# Create your views here.
def get_context(request):
    settings = Profile.objects.get(user=request.user).settings
    start_date = settings.filter_start_date
    end_date = settings.filter_end_date
    statuses = settings.filter_statuses.split(',') if settings.filter_statuses else []

    order = request.GET.get('order', '-id')

    enrollments = Enrollment.objects.range(start_date, end_date)
    if statuses:
        enrollments = Enrollment.objects.filter(status__in=statuses)

    enrollments = enrollments.order_by(order if order else '-id')
    return {
        'enrollments': enrollments,
        'start_date' : start_date.strftime('%Y-%m-%d') if start_date else None,
        'end_date' : end_date.strftime('%Y-%m-%d') if end_date else None,
        'statuses': statuses,
        'order': order,
    }
def sc_enrollments(request):
    context = get_context(request)
    return render(request, 'admissions/enrollments.html', context)
def admissions(request):
    context = get_context(request)
    return render(request, 'admissions/base.html', context)

def sc_dashboard(request):
    context = {
        'percentages': {
            'category_a': 30,
            'category_b': 25,
            'category_c': 45,
        }
    }
    return render(request, 'admissions/sc_dashboard.html', context)

def sc_students(request):
    students = Student.objects.all()
    student_data = []
    for student in students:
        enrollments = Enrollment.objects.filter(student=student)
        courses = [enrollment.course.id for enrollment in enrollments]
        total_remaining_fee = sum(enrollment.remaining_fee for enrollment in enrollments)
        student_data.append({
            'id' : student.id,
            'name': student.name,
            'father_name': student.father_name,
            'courses': ', '.join(courses),
            'remaining_fee': total_remaining_fee,
            'contact': student.contact if student.contact else 'N/A',
        })
    return render(request, 'admissions/students.html', {'students': student_data})

def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                added_student = form.instance
                return JsonResponse({'success': True, 'instance' : 'student', 'name': added_student.name, 'father_name': added_student.father_name, 'phone': added_student.contact})
            return redirect('admissions')
    else:
        form = StudentForm()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'admissions/add_student.html', {'form': form})
    return render(request, 'admissions/add_student.html', {'form': form})

def add_enrollment(request):
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admissions')

    else:
        form = EnrollmentForm()
    return render(request, 'admissions/add_enrollment.html', {'form': form})

@csrf_exempt
def delete_enrollment(request, enrollment_id):
    if request.method == 'POST':
        enrollment = Enrollment.objects.get(id=enrollment_id)
        enrollment.move_to_deleted()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@csrf_exempt
def update_student(request, student_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        student = Student.objects.get(id=student_id)
        for key, val in data.items():
            setattr(student, key, val)
        student.save()
        return JsonResponse({
            'success' : True,
            'name' : student.name,
            'father_name' : student.father_name,
            'contact': student.contact,
        })

@csrf_exempt
def update_enrollment(request, enrollment_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        enrollment = Enrollment.objects.get(id=enrollment_id)
        enrollment.status = data["status"]
        enrollment.paid_fee = int(data["paid_fee"])
        enrollment.save()
        return JsonResponse({
            'success': True,
            'status': enrollment.status,
            'paid_fee': enrollment.paid_fee,
            'remaining_fee': enrollment.remaining_fee,
        })
def update_enrollment_form(request, enrollment_id):
    if request.method == 'POST':
        enrollment = Enrollment.objects.get(id=enrollment_id)
        form = EnrollmentForm(request.POST, instance= enrollment, update=True)
        if form.is_valid():
            form.save()
            return redirect('admissions')
    else:
        enrollment = Enrollment.objects.get(id=enrollment_id)
        form = EnrollmentForm(instance=enrollment, update=True)
    return render(request, 'admissions/add_enrollment.html', {'form' : form, 'enrollment_id' : enrollment_id,'is_update': True})

@csrf_exempt
def add_contact(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        phone = data.get('phone')
        if contact_exists(phone):
            return JsonResponse({'success': True, 'exists': True,'name': name, 'phone': phone})

        if not name or not phone:
            print(1)
            return JsonResponse({'success': False, 'error': 'All fields are required.'}, status=400)

        user_data = {
            'name': name,
            'phone': phone,
            'email': data.get('email'),
            'phone_type': data.get('phone_type', 'mobile'),
            'relation_type': data.get('relation_type', None),
            'relation_value': data.get('relation_value', None)
        }
        service = get_service()
        create_contact(service, user_data, group_name = 'ShortCourses')
        add_contact_cache(phone)
        return JsonResponse({'success': True, 'exists': False, 'name': name, 'phone': phone})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

def get_student(request, id):
    if request.method == 'GET':
        try:
            student = Student.objects.get(id=id)
            enrollments = Enrollment.objects.filter(student=student)
            courses = [enrollment.course.name for enrollment in enrollments]
            total_remaining_fee = sum(enrollment.remaining_fee for enrollment in enrollments)
            student_data = {
                'name': student.name,
                'father_name': student.father_name,
                'courses': ', '.join(courses),
                'remaining_fee': total_remaining_fee,
                'contact': student.contact if student.contact else 'N/A',
            }
            return JsonResponse(student_data)
        except Student.DoesNotExist:
            return JsonResponse({'error': 'Student not found'}, status=404)


def upload_file(request):
    if request.method == "POST" and request.FILES["file"]:
        uploaded = request.FILES["file"]
        save_path = os.path.join(settings.BASE_DIR, "uploads", uploaded.name)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "wb+") as f:
            for chunk in uploaded.chunks():
                f.write(chunk)
        return HttpResponse("Uploaded successfully")
    return render(request, "upload.html")

def refresh_cache(request):
    load_contacts()
    return JsonResponse({'success' : True})