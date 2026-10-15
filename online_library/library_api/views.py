from django.shortcuts import render

# Create your views here.
from datetime import timedelta

from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status, viewsets
from rest_framework.decorators import (
    action, api_view, permission_classes
)
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAdminUser
)
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .models import Book, BorrowRecord, Review, Reminder
from .serializers import (
    RegisterSerializer,
    BookSerializer,
    BorrowRecordSerializer,
    ReviewSerializer,
    ReminderSerializer,
)


@api_view(["POST"])
@permission_classes([AllowAny])
def register_user(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()

    token, _ = Token.objects.get_or_create(user=user)

    return Response(
        {
            "message": "Registration successful",
            "username": user.username,
            "token": token.key,
        },
        status=status.HTTP_201_CREATED,
    )

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve", "recommendations"]:
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        queryset = Book.objects.all()

        search = self.request.query_params.get("search")
        category = self.request.query_params.get("category")
        available = self.request.query_params.get("available")

        if search:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(author__icontains=search)
                | Q(isbn__icontains=search)
            )

        if category:
            queryset = queryset.filter(
                category__icontains=category
            )

        if available == "true":
            queryset = queryset.filter(available_copies__gt=0)

        return queryset

    @action(detail=False, methods=["get"])
    def recommendations(self, request):
        if request.user.is_authenticated:
            borrowed_categories = list(
                BorrowRecord.objects.filter(
                    student=request.user
                ).values_list("book__category", flat=True)
            )

            reviewed_categories = list(
                Review.objects.filter(
                    student=request.user
                ).values_list("book__category", flat=True)
            )

            preferred_categories = (
                borrowed_categories + reviewed_categories
            )

            if preferred_categories:
                from django.db.models import Case, When, Value, IntegerField

                books = Book.objects.filter(
                    available_copies__gt=0
                ).exclude(
                    borrow_records__student=request.user,
                    borrow_records__returned=False,
                ).annotate(
                    preference=Case(
                        *[
                            When(
                                category=category,
                                then=Value(1),
                            )
                            for category in set(preferred_categories)
                        ],
                        default=Value(0),
                        output_field=IntegerField(),
                    )
                ).order_by("-preference", "title").distinct()[:10]
            else:
                books = Book.objects.filter(
                    available_copies__gt=0
                ).order_by("-created_at")[:10]
        else:
            books = Book.objects.filter(
                available_copies__gt=0
            ).order_by("-created_at")[:10]

        return Response(BookSerializer(books, many=True).data)

    