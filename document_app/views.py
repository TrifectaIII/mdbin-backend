import hashlib, json

from django.http import JsonResponse
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
        'markdown_text': document.markdown_text,
        'published': document.published,
    })

# View for creating a new document using a post request
@csrf_exempt
@require_http_methods(['POST'])
def publishDocument(request):

    data = json.loads(request.body)

    hash = hashlib.shake_256()
    hash.update(data['text'].encode())
    hash.update(data['creator'].encode())
    keyLength = models.Document._meta.get_field('key').max_length
    key = hash.hexdigest(keyLength // 2)

    models.Document.objects.create(
        markdown_text = data['text'],
        creator = data['creator'],
        key = key
    )

    return JsonResponse({
        'key': key
    })
