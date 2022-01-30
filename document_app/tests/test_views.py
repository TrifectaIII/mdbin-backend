import json
import re

from django.test import TestCase, override_settings
from django.urls import reverse

from document_app.models import Document


# Test the getDocument route
@override_settings(RATELIMIT_ENABLE=False)
class GetDocumentTestCase(TestCase):

    # start with a document in the db already
    def setUp(self):
        Document.objects.create(
            markdown_text = '## This is my document',
            creator = 'test@test.com',
            key = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
        )

    # tests document retrieval
    def test_getDocument(self):
        response = self.client.get(reverse(
            'getDocument', 
            kwargs = {'key': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'},
        ))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content)['text'], 
            '## This is my document'
        )

    # test 404 when document does not exist
    def test_getDocument_missing(self):
        response = self.client.get(reverse(
            'getDocument', 
            kwargs = {'key': 'aaaaaaaa-aaaa-aaaa-aaaa-bbbbbbbbbbbb'},
        ))
        self.assertEqual(response.status_code, 404)


# Test the publishDocument route
@override_settings(RATELIMIT_ENABLE=False)
class PublishDocumentTestCase(TestCase):

    # tests document publish
    def test_publishDocument(self):
        response = self.client.post(
            reverse('publishDocument'),
            data = {
                'text': 'goodbye',
                'creator': 'test2@test.com',
                'recaptchaToken': 'hello',
            },
            content_type = 'application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Document.objects.count(), 1)
        try:
            data = json.loads(response.content)
        except:
            self.fail('Could not parse response as json.')
        try:
            doc = Document.objects.get(key=data['key'])
        except Document.DoesNotExist:
            self.fail('New document not found in database.')
        self.assertEqual(doc.markdown_text, 'goodbye')
        self.assertEqual(doc.creator, 'test2@test.com')
    
    # tests document publish with invalid email field
    def test_publishDocument_invalid(self):
        response = self.client.post(
            reverse('publishDocument'),
            data = {
                'text': 'goodbye',
                'creator': 'test3testcom',
                'recaptchaToken': 'hello',
            },
            content_type = 'application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'Invalid Email')
        self.assertEqual(Document.objects.count(), 0)

    # tests document publish with missing data
    def test_publishDocument_incomplete(self):

        # test missing text
        response = self.client.post(
            reverse('publishDocument'),
            data = {
                'creator': 'test4@test.com',
                'recaptchaToken': 'hello',
            },
            content_type = 'application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'Required Field Missing or Empty')
        self.assertEqual(Document.objects.count(), 0)
        response = self.client.post(
            reverse('publishDocument'),
            data = {
                'text': '',
                'creator': 'test4@test.com',
                'recaptchaToken': 'hello',
            },
            content_type = 'application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'Required Field Missing or Empty')
        self.assertEqual(Document.objects.count(), 0)

        # test missing creator
        response = self.client.post(
            reverse('publishDocument'),
            data = {
                'text': 'hello',
                'recaptchaToken': 'hello',
            },
            content_type = 'application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'Required Field Missing or Empty')
        self.assertEqual(Document.objects.count(), 0)
        response = self.client.post(
            reverse('publishDocument'),
            data = {
                'text': 'hello',
                'creator': '',
                'recaptchaToken': 'hello',
            },
            content_type = 'application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'Required Field Missing or Empty')
        self.assertEqual(Document.objects.count(), 0)

        # test missing recaptchaToken
        response = self.client.post(
            reverse('publishDocument'),
            data = {
                'text': 'hello',
                'creator': 'test4@test.com',
            },
            content_type = 'application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'Required Field Missing or Empty')
        self.assertEqual(Document.objects.count(), 0)
        response = self.client.post(
            reverse('publishDocument'),
            data = {
                'text': 'hello',
                'creator': 'test4@test.com',
                'recaptchaToken': '',
            },
            content_type = 'application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'Required Field Missing or Empty')
        self.assertEqual(Document.objects.count(), 0)
