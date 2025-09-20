from django.db import models
from django.utils import timezone
from datetime import timedelta

class Course(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=20)
    fee = models.IntegerField()

    def __str__(self):
        return self.id

class Student(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=40)
    father_name = models.CharField(max_length=40)
    contact = models.CharField(max_length=20, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.id:
            max_id = Student.objects.aggregate(models.Max('id'))['id__max'] or 0
            self.id = max_id + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id}. {self.name} (S.O {self.father_name})"

class MonthModelManager(models.Manager):
    def range(self, start_date, end_date):
        return self.filter(start_date__gte=start_date, start_date__lte=end_date)


class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('Completed', 'Completed'),
        ('Hold', 'Hold'),
        ('Left', 'Left'),
        ('Pending', 'Pending')
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    timing = models.TimeField()
    start_date = models.DateField()

    paid_fee = models.IntegerField(default=0)
    discount = models.IntegerField(default=0, blank=True)
    remaining_fee = models.IntegerField(blank=True)

    reference = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    objects = MonthModelManager()

    def save(self, *args, **kwargs):
        self.remaining_fee = self.course.fee - self.discount - self.paid_fee
        super().save(*args, **kwargs)

    def move_to_deleted(self):
        DeletedEnrollment.objects.create(
            student=self.student,
            course=self.course,
            timing=self.timing,
            start_date=self.start_date,
            paid_fee=self.paid_fee,
            discount=self.discount,
            remaining_fee=self.remaining_fee,
            reference=self.reference,
            status=self.status,
            created_at=self.created_at,
        )
        self.delete()

    def __str__(self):
        return f"{self.student.name} Enrolled in {self.course.id}"

class DeletedEnrollment(models.Model):
    STATUS_CHOICES = [
        ('Completed', 'Completed'),
        ('Hold', 'Hold'),
        ('Left', 'Left'),
        ('Pending', 'Pending')
    ]

    student = models.ForeignKey("Student", on_delete=models.SET_NULL, null=True)
    course = models.ForeignKey("Course", on_delete=models.SET_NULL, null=True)
    timing = models.TimeField()
    start_date = models.DateField()

    paid_fee = models.IntegerField(default=0)
    discount = models.IntegerField(default=0, blank=True)
    remaining_fee = models.IntegerField(blank=True)

    reference = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Pending")
    created_at = models.DateTimeField()
    deleted_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"[DELETED-{self.deleted_at}] {self.student} - {self.course} "