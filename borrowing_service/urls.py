from rest_framework import routers
from django.urls import path
from borrowing_service.views import BorrowingViewSet, PaymentViewSet, create_checkout_session, payment_success

# router = routers.DefaultRouter()
# router.register("payments", PaymentViewSet)


urlpatterns = [
    path("borrowings/", BorrowingViewSet.as_view({"get": "list", "post": "create"}), name="borrowings-list"),
    path("borrowings/<int:pk>/", BorrowingViewSet.as_view({"get": "retrieve"}), name="borrowings-detail"),
    path("borrowings/<int:pk>/return/", BorrowingViewSet.as_view({"post": "return_book"}), name="borrowings-return"),
    path('payments/', PaymentViewSet.as_view({'get': 'list'}), name='payments-list'),
    path('payments/<int:pk>/', PaymentViewSet.as_view({'get': 'retrieve'}), name='payments-detail'),
    path('payments/create-checkout-session/', create_checkout_session),
    path('payments/success/', payment_success, name='payment_success'),

]

app_name = "borrowing_service"
