from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from ..mixins import BookCreateUpdateMixin, BookRetrieveMixin, BookListMixin
from .serializers import BookSerializer
from ..models import Book


class BookAPIView(APIView):
    model = Book
    serializer_class = BookSerializer
    renderer_classes = [TemplateHTMLRenderer]


class BookListAPIView(BookListMixin, BookAPIView, ListAPIView):
    """
    List all books
    Available filters: published_date, author (aka author__name)
    Available ordering: published_date
    """
    template_name = 'books/list.html'

    filter_backends = [OrderingFilter]
    ordering_fields = ['published_date']

    def get(self, request, *args, **kwargs):
        books = self.get_queryset()
        serialized_books = self.get_serializer(books, many=True)
        context = {
            'books': serialized_books.data
        }
        return Response(context, status=status.HTTP_200_OK)


class BookRetrieveAPIView(BookRetrieveMixin, BookAPIView, RetrieveAPIView):
    """
    Retrieve a book by book_id get parameter.
    """
    template_name = 'books/single.html'

    def get(self, request, *args, **kwargs):
        book = self.get_object(request, *args, **kwargs)
        serialized_book = self.get_serializer(book, many=False)
        context = {
            'book': serialized_book.data
        }
        return Response(context, status=status.HTTP_200_OK)


class BookCreateUpdateAPIView(BookCreateUpdateMixin, CreateAPIView):
    """
    Concrete view for creating and/or updating model instances.
    """
    def post(self, request, *args, **kwargs):
        return self.create_or_update(request, *args, **kwargs)
