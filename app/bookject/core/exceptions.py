from rest_framework import status
from rest_framework.exceptions import APIException


class GetResponseError(APIException):
    """Raised when getting response has failed"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Failed to get response.'


class ResponseDeserializationError(APIException):
    """Raised when response deserialization has failed"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Response deserialization has failed.'
