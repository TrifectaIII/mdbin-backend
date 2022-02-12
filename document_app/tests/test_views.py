import uuid, json
from django.test import TestCase, override_settings
from django.urls import reverse

from ..models import Document


# Test the getDocument route
class GetDocumentTestCase(TestCase):

    # start with a document in the db already
    def setUp(self):
        Document.objects.create(
            key = uuid.UUID('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'),
            markdown_text = '## This is my document',
            creator = 'test@test.com',
        )

    # tests document retrieval
    def test_getDocument(self):
        path = reverse('DocumentView') \
            + '?key=aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content)['text'], 
            '## This is my document',
        )
        self.assertEqual(
            type(json.loads(response.content)['published']),
            int,
        )

    # test 404 when document does not exist
    def test_getDocument_missing(self):
        path = reverse('DocumentView') \
            + '?key=bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'
        response = self.client.get(path)
        self.assertEqual(response.status_code, 404)


# Test the publishDocument route
# disable ratelimit during tests
@override_settings(RATELIMIT_ENABLE=False)
class PublishDocumentTestCase(TestCase):

    # tests document publish
    def test_publishDocument(self):
        response = self.client.post(
            path = reverse('DocumentView'),
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
           key =  uuid.UUID(data['key'])
        except ValueError:
            self.fail('Could not parse key from hex to bytes')
        try:
            doc = Document.objects.get(key = key)
        except Document.DoesNotExist:
            self.fail('New document not found in database.')
        self.assertEqual(doc.markdown_text, 'goodbye')
        self.assertEqual(doc.creator, 'test2@test.com')
    
    # tests document publish with invalid email field
    def test_publishDocument_invalid(self):

        # test invalid email syntax
        response = self.client.post(
            path = reverse('DocumentView'),
            data = {
                'text': 'goodbye',
                'creator': 'test3testcom',
                'recaptchaToken': 'hello',
            },
            content_type = 'application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'Invalid Email Syntax')
        self.assertEqual(Document.objects.count(), 0)

        # test invalid domain name
        response = self.client.post(
            path = reverse('DocumentView'),
            data = {
                'text': 'goodbye',
                'creator': 'invalid@invalid.invalid',
                'recaptchaToken': 'hello',
            },
            content_type = 'application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'Invalid Email Domain')
        self.assertEqual(Document.objects.count(), 0)

    # tests document publish with missing data
    def test_publishDocument_incomplete(self):

        # test missing text
        response = self.client.post(
            path = reverse('DocumentView'),
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
            path = reverse('DocumentView'),
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
            path = reverse('DocumentView'),
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
            path = reverse('DocumentView'),
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
            path = reverse('DocumentView'),
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
            path = reverse('DocumentView'),
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

    # tests document publish with ratelimiting
    # enable ratelimit during this test
    @override_settings(RATELIMIT_ENABLE=True)
    def test_publishDocument_ratelimit(self):

        # first post should succeed
        response = self.client.post(
            path = reverse('DocumentView'),
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
           key =  uuid.UUID(data['key'])
        except ValueError:
            self.fail('Could not parse key from hex to bytes')
        try:
            doc = Document.objects.get(key = key)
        except Document.DoesNotExist:
            self.fail('New document not found in database.')
        self.assertEqual(doc.markdown_text, 'goodbye')
        self.assertEqual(doc.creator, 'test2@test.com')

        # do a bunch more and one should fail eventually
        final = False
        for i in range(1000):
            response = self.client.post(
                path = reverse('DocumentView'),
                data = {
                    'text': 'goodbye2',
                    'creator': 'test5@test.com',
                    'recaptchaToken': 'hello2',
                },
                content_type = 'application/json',
            )
            if (response.status_code != 200):
                final = response
                break
        self.assertTrue(final)
        self.assertEqual(final.status_code, 429)
        self.assertEqual(
            final.content,
            b'Ratelimit exceeded. Please try again later.',
        )