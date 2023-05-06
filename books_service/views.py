from rest_framework import viewsets

from books_service.models import Book
from books_service.serializers import BookListCreateSerializer, BookDetailSerializer


class BookViewSet(viewsets.ModelViewSet):
    serializer_class = BookListCreateSerializer
    queryset = Book.objects.all()

    def get_serializer_class(self):
        if self.action in ("PUT", "PATCH", "DELETE"):
            return [BookDetailSerializer]
        return self.serializer_class
