import logging
from datetime import datetime

from django.http import Http404
from rest_framework.generics import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from ..core.utils import deserialize_response, get_response, BulkCreateManager
from .models import Book, Author, Category
from .exceptions import BooksNotFound, IncorrectPublishedDateOfBook, BookDoesNotExists, BookParserException, \
    InvalidQueryParameterInBody

# Get an instance of a logger
logger = logging.getLogger(__name__)


class BookDownloader:
    source_url = "https://www.googleapis.com/books/v1/volumes?q="

    def __init__(self, query):

        # "q" parameter from POST body
        self.query = query

        # A json response placeholder
        self.response = None

        # Dictionaries of books from json document and of book currently being created
        self.books, self.book_dict = {}, {}

        # List of ids of books from json document
        self.books_ids = []

        # Currently iterated book from json document
        self.book = None

        # List of not existing and already existing in database books
        self.existing, self.not_existing = [], []

        # URL from which json is downloaded
        self.url = self.source_url + (self.query or '')

        # New books bulk insert manager
        self.bulk_manager = BulkCreateManager()

        # List of books to update
        self.objects_to_update = []

        # Lists of categories and authors from ManyToMany relations to add after saving objects
        self.book_category_m2m_list, self.book_author_m2m_list = [], []

        # Lists of created/updated authors and categories (m2m relation of books)
        self.authors, self.categories = [], []

    def get_books(self):
        """
        Get and deserialize response.
        Return books dictionary if success, else if failed raise BooksNotFound.
        """

        # Get and set response. May raise GetResponseError.
        self.set_response()

        volumes = deserialize_response(self.response)
        if 'items' in volumes:
            books = volumes['items']
            return books
        else:
            logger.error(f"Books not found")
            raise BooksNotFound

    def get_information(self):
        """
        Get book information.
        Create or update many 2 many relation objects.
        """
        self.book_dict['book_id'] = self.book['id']

        if 'title' in self.book['volumeInfo']:
            self.book_dict['title'] = self.book['volumeInfo']['title']

        # When book is created, M2M related authors/categories need to be added later due to bulk insert
        # When book is updated, authors/categories can be added immediately (no bulk operation)
        # Authors/Categories to be added to self.book_dict later
        if 'authors' in self.book['volumeInfo']:
            self.authors = self.update_or_create_authors()
        if 'categories' in self.book['volumeInfo']:
            self.categories = self.update_or_create_categories()
        if 'imageLinks' in self.book['volumeInfo']:
            if 'thumbnail' in self.book['volumeInfo']['imageLinks']:
                self.book_dict['thumbnail'] = self.book['volumeInfo']['imageLinks']['thumbnail']
        if 'publishedDate' in self.book['volumeInfo']:
            self.book_dict['published_date'] = self.get_published_date()
        if 'averageRating' in self.book['volumeInfo']:
            self.book_dict['average_rating'] = self.book['volumeInfo']['averageRating']
        if 'ratingsCount' in self.book['volumeInfo']:
            self.book_dict['ratings_count'] = self.book['volumeInfo']['ratingsCount']

    def update_or_create_authors(self):
        """
        Update or create Author objects and return a list of these objects.
        """
        objects = []
        authors = self.book['volumeInfo']['authors']
        for author in authors:
            obj, created = Author.objects.update_or_create(name=author)
            objects.append(obj)

        return objects

    def update_or_create_categories(self):
        """
        Update or create Category objects and return a list of these objects.
        """
        objects = []
        categories = self.book['volumeInfo']['categories']
        for category in categories:
            obj, created = Category.objects.update_or_create(name=category)
            objects.append(obj)
        return objects

    def get_published_date(self):
        """
        Get published date from books dict which is based on source json.
        Set exact_date if provided full date
        """
        published_date_str = self.book['volumeInfo']['publishedDate']
        try:
            if len(published_date_str) == 4:
                pattern = '%Y'
            else:
                pattern, self.book_dict['exact_date'] = '%Y-%m-%d', True

            published_date = datetime.strptime(published_date_str, pattern)
            return published_date

        except (ValueError, TypeError) as err:
            logger.error(f'Incorrect published date "{published_date_str}" for book - {err}')
            raise IncorrectPublishedDateOfBook

    def get_books_ids(self):
        """
        Get new books ids from book dict.
        Purpose: To check later if already exists in the database
        """
        ids = []
        for book in self.books:
            if 'id' in book:
                ids.append(book['id'])
        return ids

    def get_existing(self):
        """
        Return list of ids of already existing books in database
        """
        return list(Book.get_ids_which_already_exists(self.books_ids))

    def get_not_existing(self):
        """
        Return list of ids of not existing yet books,
        which is based on list of new and already existing books
        """
        return [item for item in self.books_ids if item not in self.existing]

    def create_new_books(self):
        """
        Commit bulk inserts
        """
        self.bulk_manager.done()

    def create_m2m_book_authors(self):
        """
        Create many2many relation objects for authors of the books
        """
        BookAuthor = Book.authors.through
        BookAuthor.objects.bulk_create(
            [BookAuthor(
                book_id=book.id,
                author_id=author.id
            )
                for book, author in self.book_author_m2m_list]
        )
        self.book_author_m2m_list = []

    def create_m2m_book_categories(self):
        """
            Create many2many relation objects for categories of the books
        """
        BookCategory = Book.categories.through
        BookCategory.objects.bulk_create(
            [BookCategory(
                book_id=book.id,
                category_id=category.id
            )
                for book, category in self.book_category_m2m_list]
        )
        self.book_category_m2m_list = []

    def create_m2m_objects(self):
        """
        Create many2many relation objects of the books
        """

        self.create_m2m_book_authors()
        self.create_m2m_book_categories()

    def update_existing_book(self):
        """
        Update existing book.
        Raise Http404 and BookDoesNotExists if book does not exists.
        """
        try:
            # Try to get book object to update - raise an exception failed
            updated_book = get_object_or_404(Book, book_id=self.book_dict['book_id'])

            # Update modified book
            updated_book.save(update_fields=list(self.book_dict.keys()))

            # Update m2m relations
            updated_book.authors.set(self.authors)
            updated_book.categories.set(self.categories)

        except Http404 as err:
            logger.error(f"Book {self.book_dict['id']} does not exists - {err}")
            raise BookDoesNotExists

    def manage_not_existing_book(self):
        """
        Manage not existing book:
        - create new book and add to bulk manager
        - commit with bulk create if batch size is exceeded
        - create authors and categories ManyToMany relation objects and add to M2M lists
        - commit authors and categories objects if books objects has been committed
        """
        # Create new Book object, wait with commit
        new_book = Book(**self.book_dict)

        # Add newly created book to bulk insert manager
        # Commit when batch chuck size exceeded (init parameter)
        # Else add book to waiting queue
        self.bulk_manager.add(new_book)

        # Add authors and categories to m2m lists in order to create object
        self.set_m2m_lists(new_book)

    def manage_existing_book(self):
        """
        Set M2M fields (authors, categories) and update existing book
        """
        self.update_existing_book()

    def set_response(self):
        self.response = get_response(self.url)

    def set_books_ids(self):
        self.books_ids = self.get_books_ids()

    def set_books(self):
        self.books = self.get_books()

    def set_existing_books(self):
        self.existing = self.get_existing()

    def set_not_existing_books(self):
        self.not_existing = self.get_not_existing()

    def set_m2m_lists(self, new_book):
        self.book_author_m2m_list += [[new_book, author] for author in self.authors]
        self.book_category_m2m_list += [[new_book, category] for category in self.categories]

    def perform_create(self):

        self.set_books()  # Try to get books from source and raise BooksNotFound if failed
        self.set_books_ids()  # Get ids of all new books
        self.set_existing_books()  # Mark already existing books
        self.set_not_existing_books()  # Mark new books

        # Gather book information in loop
        for book in self.books:
            self.book = book

            # Get book data - missing anything critical breaks iteration
            try:
                self.get_information()
            except KeyError as err:
                logger.error(f"Incorrect input data. Critical book data is not provided - {err}")
                raise BookParserException

            if self.book_dict['book_id'] in self.existing:
                self.manage_existing_book()
            else:
                self.manage_not_existing_book()

        # Try to bulk create new books and m2m relation objects if new books exist
        # New objects could be already created if batch size was reached
        if self.not_existing:
            self.create_new_books()
            self.create_m2m_objects()


class BookCreateUpdateMixin(object):
    """
    Create/update Book model instances.
    """

    @staticmethod
    def get_parameter(request):
        """
        Get and set POST request "q" parameter.
        Return value of parameter if success, else raise InvalidQueryParameterInBody exception
        """

        query = request.POST.get("q", "")
        if not query:
            raise InvalidQueryParameterInBody
        return query

    def create_or_update(self, request, *args, **kwargs):
        """
        Process request to create/update books.
        Return Response with status code 201 if success.
        """

        # Get query "q" parameter. May raise InvalidQueryParameterInBody exception
        query = self.get_parameter(request)

        BookDownloader(query=query).perform_create()
        return Response(f"Success: q={query}", status=status.HTTP_201_CREATED)
