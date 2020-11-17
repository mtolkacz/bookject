from django.shortcuts import render

from . import apiv1


def index(request):
    """
    A homepage of Bookject - Simple book API
    """
    return render(request, 'books/index.html')
