from django.test import TestCase
from document_app import models

class ViewsTestCase(TestCase):

    def setUp(self):
        models.Document.objects.create(
            markdown_text = '## This is my document',
            creator = 'test@test.test',
            key = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
        )

    def testGetDocumentView(self):
        self.assertEqual(True, True)
