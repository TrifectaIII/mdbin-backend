import uuid
from django.db import models


class Document(models.Model):

    # the uuid key used for retrieval
    key = models.UUIDField(
        primary_key = True, 
        default = uuid.uuid4,
        editable = False,
    )

    # the markdown text of the document
    markdown_text = models.TextField()

    # the email of the document creator
    creator = models.EmailField()

    # when this document is published
    published = models.DateTimeField(auto_now_add = True)
