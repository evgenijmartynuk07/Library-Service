import asyncio
import datetime
import telegram
import os
import datetime
from celery.utils.time import timezone
from django.http import HttpResponse, HttpResponseRedirect
from dotenv import load_dotenv
import stripe
from django.views.decorators.csrf import csrf_exempt
from flask import Flask, redirect
from django.db.models import QuerySet
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from django.db import transaction

from books_service.models import Book
from borrowing_service.models import Borrowing, Payment
from borrowing_service.serializers import BorrowingListSerializer, BorrowingDetailSerializer, BorrowingCreateSerializer, \
    BorrowingReturnSerializer, PaymentListSerializer, PaymentDetailSerializer

load_dotenv()
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
bot = telegram.Bot(token=BOT_TOKEN)

app = Flask(__name__)
stripe.api_key = os.environ.get("STRIPE_KEY")


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsAuthenticated,)
    queryset = Borrowing.objects.select_related("book", "user")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        if self.action == "create":
            return BorrowingCreateSerializer
        if self.action == "return_book":
            return BorrowingReturnSerializer
        return BorrowingListSerializer

    def get_queryset(self) -> QuerySet:
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data["user"] = request.user.id
        book = Book.objects.get(id=request.data.get("book"))
        if book.inventory <= 0:
            raise "No book available"
        with transaction.atomic():
            book.inventory -= 1
            book.save()
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)

            async def send_message(text):
                await bot.send_message(chat_id=CHAT_ID, text=text)
            asyncio.run(send_message(serializer.data))

            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )

    @action(
        methods=["POST"],
        detail=True,
        url_path="return",
    )
    def return_book(self, request, pk):
        """Create a new comment for a specific post."""
        borrowing = self.get_object()
        book = Book.objects.get(borrowings=pk)
        with transaction.atomic():
            if borrowing.actual_return_date is None:
                book.inventory += 1
                book.save()
                borrowing.actual_return_date = datetime.date.today()
                borrowing.save()
                return Response(status=status.HTTP_200_OK)
            return Response(status=status.HTTP_403_FORBIDDEN)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "is_active",
                type=OpenApiTypes.BOOL,
                description="Filter by is active now( True or False)",
            ),
            OpenApiParameter(
                "user_id",
                type=OpenApiTypes.INT,
                description="Filter by user id for admin user only",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        is_active = self.request.query_params.get("is_active")
        user_id = self.request.query_params.get("user_id")
        if is_active:
            if is_active.lower() == "true":
                queryset = queryset.filter(actual_return_date=None)
            else:
                queryset = queryset.exclude(actual_return_date=None)
        if request.user.is_staff and user_id:
            queryset = queryset.filter(user=user_id)

        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PaymentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsAuthenticated,)
    queryset = Payment.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PaymentDetailSerializer
        return PaymentListSerializer

    def get_queryset(self):
        queryset = Payment.objects.all()
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(borrowing__user=self.request.user)


@app.route("/create-checkout-session/?borrowing_id=<int:pk>", methods=["GET"])
def create_checkout_session(request):
    borrowing_id = request.GET['borrowing_id']
    borrowing = Borrowing.objects.get(id=borrowing_id)
    payment = Payment.objects.create(
        borrowing=borrowing,
        money_to_pay=borrowing.total_fine_amount,
        type="PAYMENT",
    )
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': borrowing.book.title,
                },
                'unit_amount': int(payment.money_to_pay * 100),  # stripe requires amount in cents
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url='http://127.0.0.1:8000/api/payments/success/?session_id={CHECKOUT_SESSION_ID}',
        cancel_url='http://127.0.0.1:8000/cancel',
        metadata={
            'payment_id': payment.id  # save the payment id in metadata for later retrieval
        }
    )
    # update payment model with session_id and session_url
    payment.session_id = session.id
    payment.session_url = session.url
    payment.save()

    return HttpResponseRedirect(session.url)


@csrf_exempt
def payment_success(request):
    session_id = request.GET['session_id']

    with transaction.atomic():
        checkout_session = stripe.checkout.Session.retrieve(session_id)

        payment_id = checkout_session.metadata['payment_id']
        payment = Payment.objects.get(id=payment_id)

        payment.session_id = checkout_session.payment_intent
        payment.money_to_pay = checkout_session.amount_total / 100
        payment.status = "PAID"
        payment.type = "FINE"
        payment.save()

        borrowing = payment.borrowing
        borrowing.actual_return_date = datetime.date.today()
        borrowing.save()

        return HttpResponseRedirect('../../payments/')
