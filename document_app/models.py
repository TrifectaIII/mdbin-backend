from django.db import models


class Document(models.Model):

    # the uuid key used for retrieval
    key = models.CharField(primary_key=True, max_length = 36)

    # the markdown text of the document
    markdown_text = models.TextField()

    # the email of the document creator
    creator = models.EmailField()

    # when this document is published
    published = models.DateTimeField(auto_now_add = True)
