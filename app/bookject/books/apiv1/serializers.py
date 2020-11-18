from rest_framework import serializers

from ..models import Book, Category, Author


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = [
            'name'
        ]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'name',
        ]


class BookSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    authors = AuthorSerializer(many=True, read_only=True)

    def to_representation(self, instance):
        representation = super(BookSerializer, self).to_representation(instance)
        representation['published_date'] = instance.published_date.strftime('%Y')
        return representation

    class Meta:
        model = Book
        fields = [
            'book_id',
            'title',
            'authors',
            'published_date',
            'categories',
            'average_rating',
            'ratings_count',
            'thumbnail'
        ]
