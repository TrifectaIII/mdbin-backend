import uuid, json, requests
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from email_validator import validate_email, EmailNotValidError
from ratelimit.decorators import ratelimit

from .models import Document


# View for retrieving a document based on key
@require_http_methods(['GET']) # existing documents can only be retrieved
def getDocument(request, key):
    document = get_object_or_404(Document, key = key)
    return JsonResponse({
        'text': document.markdown_text,
        'published': document.published,
    })

# View for creating a new document using a post request
@csrf_exempt # disable csrf for api post view
@require_http_methods(['POST']) # must use post to publish
@ratelimit(key = 'ip', rate = '1/m', block = True) # ratelimit publish requests
def publishDocument(request):

    # extract data from request body
    data = json.loads(request.body)

    # verify that request contains needed fields
    if (('text' not in data)
    or (not data['text'])
    or ('creator' not in data)
    or (not data['creator'])
    or ('recaptchaToken' not in data)
    or (not data['recaptchaToken'])):
        return HttpResponse('Required Field Missing or Empty', status = 400)

    # verify that email address is valid
    try:
        email = validate_email(data['creator']).email
    except EmailNotValidError as e:
        return HttpResponse('Invalid Email', status = 400)

    # verify recaptcha token with key
    r = requests.post(
        url = settings.RECAPTCHA_V2_URL, 
        data = {
            'secret': settings.RECAPTCHA_V2_SECRET_KEY,
            'response': data['recaptchaToken'],
        },
    )
    if (not 'success' in r.json() or not r.json()['success']):
        return HttpResponse('Recaptcha Failure', status = 401)

    # create a key with uuid library
    key = str(uuid.uuid1())

    # add document to database
    Document.objects.create(
        markdown_text = data['text'],
        creator = email,
        key = key,
    )

    return JsonResponse({'key': key})
