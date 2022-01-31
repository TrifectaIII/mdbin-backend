import uuid
from django.db import models


class Document(models.Model):

    # the uuid key used for retrieval
    key = models.BinaryField(max_length = 16)

    # the markdown text of the document
    markdown_text = models.TextField()

    # the email of the document creator
    creator = models.EmailField()

    # when this document is published
    published = models.DateTimeField(auto_now_add = True)

    # returns the hex string of the uuid key
    def keyHex(self):
        return str(uuid.UUID(bytes = self.key))
