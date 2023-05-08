from rest_framework import serializers

from borrowing_service.models import Borrowing


class BorrowingListSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source="book.title", read_only=True)
    book_author = serializers.CharField(source="book.author", read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book_title",
            "book_author",
            "user"
        )


class BorrowingDetailSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source="book.title")
    book_author = serializers.CharField(source="book.author")
    book_cover = serializers.CharField(source="book.cover")
    book_daily_fee = serializers.CharField(source="book.daily_fee")

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book_title",
            "book_author",
            "book_cover",
            "book_daily_fee",
            "user"
        )

        read_only_fields = (
            "book_title",
            "book_author",
            "book_cover",
            "book_daily_fee",
            "user"
        )


class BorrowingCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = ("book", "expected_return_date", "user")
        read_only_fields = ("user",)

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user
        return super().create(validated_data)
