from rest_framework import serializers

from books_service.models import Book


class BookListCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = "__all__"


class BookDetailSerializer(serializers.ModelSerializer):
    borrowings = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="id"
    )

    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "author",
            "cover",
            "inventory",
            "daily_fee",
            "borrowings",
        )
