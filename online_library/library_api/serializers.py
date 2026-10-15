from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Book, BorrowRecord, Review, Reminder


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, min_length=8
    )

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = "__all__"


class BorrowRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(
        source="student.username", read_only=True
    )
    book_title = serializers.CharField(
        source="book.title", read_only=True
    )
    is_overdue = serializers.ReadOnlyField()

    class Meta:
        model = BorrowRecord
        fields = "__all__"
        read_only_fields = [
            "student", "issue_date", "returned", "return_date"
        ]


class ReviewSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(
        source="student.username", read_only=True
    )

    class Meta:
        model = Review
        fields = "__all__"
        read_only_fields = ["student", "created_at"]

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError(
                "Rating must be between 1 and 5."
            )
        return value


class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = "__all__"
        read_only_fields = ["student", "created_at"]

        