from django.contrib import admin

# Register your models here.

from .models import Book, BorrowRecord, Review, Reminder


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "title", "author", "category",
        "total_copies", "available_copies"
    )
    search_fields = ("title", "author", "isbn")
    list_filter = ("category",)


@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = (
        "student", "book", "issue_date",
        "due_date", "returned"
    )
    list_filter = ("returned", "due_date")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("book", "student", "rating", "created_at")


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ("student", "message", "read", "created_at")