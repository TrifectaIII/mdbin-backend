import uuid
from django.db import models
from django.conf import settings


class Document(models.Model):

    # the uuid key used for retrieval
    key = models.UUIDField(
        primary_key = True, 
        default = uuid.uuid4,
        editable = False,
    )

    # the markdown text of the document
    markdown_text = models.TextField(
        max_length = settings.DOCUMENT_MAX_LENGTH,
    )

    # the email of the document creator
    creator = models.EmailField()

    # when this document is published
    published = models.DateTimeField(auto_now_add = True)

    # string method for printing
    def __str__(self):
        return str(self.key)

    # convert published datetime to unix timestamp in ms
    def publishedTimestampMs(self):
        return int(self.published.timestamp() * 1000)
