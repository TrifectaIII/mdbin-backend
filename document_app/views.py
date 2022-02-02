import uuid, json, requests
from django.conf import settings
from django.http import Http404, JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from email_validator import validate_email, \
EmailNotValidError, EmailSyntaxError, EmailUndeliverableError
from ratelimit.decorators import ratelimit

from .models import Document


# View for retrieving a document based on key
@require_http_methods(['GET']) # existing documents can only be retrieved
def getDocument(request, key):

    # convert url param to uuid
    try:
        keyUUID = uuid.UUID(key)
    except ValueError:
        raise Http404
    
    # fetch document from db
    document = get_object_or_404(Document, key = keyUUID)

    # return information
    return JsonResponse({
        'text': document.markdown_text,
        'published': document.publishedTimestampMs(),
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
    or ('creator' not in data)
    or ('recaptchaToken' not in data)
    or (not data['text'])
    or (not data['creator'])
    or (not data['recaptchaToken'])):
        return HttpResponse('Required Field Missing or Empty', status = 400)

    # verify that email address is valid
    try:
        email = validate_email(data['creator']).email
    except EmailNotValidError as e:
        if isinstance(e, EmailSyntaxError):
            return HttpResponse('Invalid Email Syntax', status = 400)
        elif isinstance(e, EmailUndeliverableError):
            return HttpResponse('Invalid Email Domain', status = 400)
        return HttpResponse('Invalid Email', status = 400)

    # verify recaptcha token with key
    r = requests.post(
        url = settings.RECAPTCHA_V2_URL, 
        data = {
            'secret': settings.RECAPTCHA_V2_SECRET_KEY,
            'response': data['recaptchaToken'],
        },
    ).json()
    if (not 'success' in r or not r['success']):
        return HttpResponse('Recaptcha Failure', status = 401)

    # add document to database
    document = Document.objects.create(
        markdown_text = data['text'],
        creator = email,
    )

    # return key to client
    return JsonResponse({'key': str(document.key)})
