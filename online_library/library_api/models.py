from django.db import models

# Create your models here.

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=150)
    category = models.CharField(max_length=100)
    isbn = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    published_year = models.PositiveIntegerField(
        null=True, blank=True
    )
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class BorrowRecord(models.Model):
    student = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="borrow_records"
    )
    book = models.ForeignKey(
        Book, on_delete=models.PROTECT,
        related_name="borrow_records"
    )
    issue_date = models.DateField(default=timezone.localdate)
    due_date = models.DateField(
        default=lambda: timezone.localdate() + timedelta(days=14)
    )
    returned = models.BooleanField(default=False)
    return_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-issue_date"]

    def __str__(self):
        return f"{self.student.username} - {self.book.title}"

    @property
    def is_overdue(self):
        return (
            not self.returned
            and self.due_date < timezone.localdate()
        )


class Review(models.Model):
    student = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="book_reviews"
    )
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE,
        related_name="reviews"
    )
    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "book"],
                name="unique_student_book_review"
            )
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.book.title}: {self.rating}/5"


class Reminder(models.Model):
    student = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="library_reminders"
    )
    borrow_record = models.ForeignKey(
        BorrowRecord, on_delete=models.CASCADE,
        related_name="reminders"
    )
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.message