import hashlib, json, datetime, requests

from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from . import models


# View for retrieving a document based on key
@csrf_exempt
@require_http_methods(['GET'])
def getDocument(request, key):
    document = get_object_or_404(models.Document, key=key)
    return JsonResponse({
        'text': document.markdown_text,
        'published': document.published,
    })

# View for creating a new document using a post request
@csrf_exempt
@require_http_methods(['POST'])
def publishDocument(request):

    # extract data from request body
    data = json.loads(request.body)

    # verify recaptcha token with key
    r = requests.post(settings.RECAPTCHA_V2_URL, data={
        'secret': settings.RECAPTCHA_V2_SECRET_KEY,
        'response': data['recaptchaToken'],
    })
    if (not r.json()['success']):
        return HttpResponse('401 Unauthorized', status=401)

    # fill hash with text, creator email and current time
    hash = hashlib.shake_256()
    hash.update(data['text'].encode())
    hash.update(data['creator'].encode())
    hash.update(str(datetime.datetime.now()).encode())

    # create the key with length based on model field length
    keyLength = models.Document._meta.get_field('key').max_length
    key = hash.hexdigest(keyLength // 2)

    models.Document.objects.create(
        markdown_text = data['text'],
        creator = data['creator'],
        key = key
    )

    return JsonResponse({'key': key})
