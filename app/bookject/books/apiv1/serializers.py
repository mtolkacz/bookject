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
            'name'
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
            'title',
            'authors',
            'published_date',
            'categories',
            'average_rating',
            'ratings_count',
            'thumbnail'
        ]

# {
#     "title": "Hobbit czyli Tam i z powrotem",
#     "authors": ["J. R. R. Tolkien"],
#     "published_date": "2004",
#     "categories": [
#         "Baggins, Bilbo (Fictitious character)"
#       ],
#     "average_rating": 5,
#     "ratings_count": 2,
#     "thumbnail": "http://books.google.com/books/content?id=YyXoAAAACAAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api",
# }