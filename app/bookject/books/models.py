from django.db import models


class Category(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
    )


class Author(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
    )


class Book(models.Model):
    book_id = models.CharField(
        max_length=12,
        unique=True,
    )
    title = models.CharField(
        max_length=200,
    )
    authors = models.ManyToManyField(
        Author,
    )
    published_date = models.DateField()
    # If published_date contains only year then set to False, else if full date then True
    exact_date = models.BooleanField(
        default=False,
    )
    categories = models.ManyToManyField(
        Category,
    )
    average_rating = models.FloatField(
        null=True,
    )
    ratings_count = models.PositiveIntegerField(
        null=True,
    )
    thumbnail = models.URLField(
        max_length=500,
    )
    created_date = models.DateTimeField(
        auto_now_add=True,
    )
    modified_date = models.DateTimeField(
        auto_now=True,
    )

    @staticmethod
    def get_ids_which_already_exists(ids):
        return Book.objects.filter(book_id__in=ids).values_list('book_id', flat=True)

