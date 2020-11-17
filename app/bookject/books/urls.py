from django.urls import path
from .views import apiv1, index

app_name = "bookject.books"

urlpatterns = [
    # /books
    # eg. /books?author=Howard&published_date=2006&published_date=1995&ordering=-published_date
    path(
        route='books',
        view=apiv1.BookListAPIView.as_view(),
        name='list',
    ),
    # /books/:pk
    # eg. /books/ML6TpwAACAAJ
    path(
        route='books/<str:book_id>',
        view=apiv1.BookRetrieveAPIView.as_view(),
        name='single',
    ),
    # /db/
    # eg. curl -X  POST -d "q=Hobbit' http://{host:8000}/db/
    path(
        route='db/',
        view=apiv1.BookCreateUpdateAPIView.as_view(),
        name='db',
    ),
    # /
    path(
        route='',
        view=index,
        name='index',
    )
]

