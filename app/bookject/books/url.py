from django.urls import path
from .apiv1 import views

urlpatterns = [
    # /books/
    path(
        route='books/',
        view=views.BookListAPIView.as_view(),
        name='book_rest_api',
    ),
    # /books/:pk/
    path(
        route='books/<int:pk>/',
        view=views.BookRetrieveAPIView.as_view(),
        name='book_rest_api',
    ),
    # /db/
    path(
        route='db/',
        view=views.BookCreateUpdateAPIView.as_view(),
        name='book_rest_api',
    ),

]

