from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser
from books_service.models import Book
from books_service.serializers import BookListCreateSerializer, BookDetailSerializer


class BookViewSet(viewsets.ModelViewSet):
    serializer_class = BookListCreateSerializer
    permission_classes = (IsAdminUser,)
    queryset = Book.objects.all()

    def get_serializer_class(self):
        if self.action in ("PUT", "PATCH", "DELETE"):
            self.serializer_class = (BookDetailSerializer,)
        return super(BookViewSet, self).get_serializer_class()

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = (AllowAny,)
        return super(BookViewSet, self).get_permissions()
