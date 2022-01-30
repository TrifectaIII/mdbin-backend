import json

from django.test import TestCase
from django.urls import reverse

from document_app import models


class ViewsTestCase(TestCase):

    # start with a document in the db already
    def setUp(self):
        models.Document.objects.create(
            markdown_text = '## This is my document',
            creator = 'test@test.test',
            key = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
        )

    # tests document retrieval
    def test_getDocument_exists(self):
        response = self.client.get(reverse(
                'getDocument', 
                kwargs = {
                    'key': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
                },
        ))
        self.assertEqual(
            response.status_code, 
            200
        )
        self.assertEqual(
            json.loads(response.content)['text'], 
            '## This is my document'
        )

    # test 404 when document does not exist
    def test_getDocument_missing(self):
        response = self.client.get(reverse(
                'getDocument', 
                kwargs = {
                    'key': 'aaaaaaaa-aaaa-aaaa-aaaa-bbbbbbbbbbbb',
                },
        ))
        self.assertEqual(
            response.status_code, 
            404
        )
