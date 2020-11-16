from django_filters.rest_framework import DjangoFilterBackend, filters
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.filters import OrderingFilter


from ..mixins import BookCreateUpdateMixin
from .serializers import BookSerializer
from ..models import Book


class BookListAPIView(ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_fields = ['published_date']
    ordering_fields = ['published_date']  # todo add ordering by year, currently works by datetime


class BookRetrieveAPIView(RetrieveAPIView):
    # todo
    pass


class BookCreateUpdateAPIView(BookCreateUpdateMixin, CreateAPIView):
    """
    Concrete view for creating and/or updating model instances.
    """

    def post(self, request, *args, **kwargs):
        return self.create_or_update(request, *args, **kwargs)


