from rest_framework import status
from rest_framework.exceptions import APIException


class InvalidQueryParameterInBody(APIException):
    """
    Raised when parameter passed in body is invalid
    In case of books, there is no 'q' parameter provided.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid key has been passed in request body.'


class BookDownloaderException(APIException):
    """
    Raised when books downloading has been failed
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'BookDownloader exception.'


class BookDoesNotExists(APIException):
    """
    Raised when no books has been found in source
    """
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Books not exists.'


class BooksNotFound(APIException):
    """
    Raised when no books has been found in source
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Books not found.'


class BookParserException(APIException):
    """
    Raised when response deserialization has been failed
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Incorrect input data for book.'


class IncorrectPublishedDateOfBook(APIException):
    """Raised when response deserialization has been failed"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Incorrect published date for book'

