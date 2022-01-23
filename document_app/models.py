from django.db import models


class Document(models.Model):

    # the markdown text of the document
    markdown_text = models.TextField()

    # the email of the document creator
    creator = models.EmailField()

    # when this document is published
    published = models.DateTimeField(auto_now_add=True)

    # the hash id used for retrieval
    identifier = models.CharField(unique=True, max_length=10)
