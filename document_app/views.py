import uuid, json, requests
from django.conf import settings
from django.http import Http404, JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from ratelimit.decorators import ratelimit
from email_validator import validate_email, \
EmailNotValidError, EmailSyntaxError, EmailUndeliverableError

from .models import Document


@method_decorator(csrf_exempt, name='dispatch')
class DocumentView(View):

    http_method_names = ['get', 'post']

    def get(self, request):

        # extract key parameter
        key = request.GET.get('key', '')

        # convert key to uuid
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
    
    # ratelimit publish requests
    @method_decorator(ratelimit(key = 'ip', rate = '1/m', block = True))
    def post(self, request):

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

        # verify that email address is syntactically valid and that domain exists
        try:
            email = validate_email(data['creator']).email
        except EmailNotValidError as e:
            if isinstance(e, EmailSyntaxError):
                return HttpResponse('Invalid Email Syntax', status = 400)
            elif isinstance(e, EmailUndeliverableError):
                return HttpResponse('Invalid Email Domain', status = 400)
            return HttpResponse('Invalid Email.', status = 400)

        # verify recaptcha token with key
        res = requests.post(
            url = settings.RECAPTCHA_V2_URL, 
            data = {
                'secret': settings.RECAPTCHA_V2_SECRET_KEY,
                'response': data['recaptchaToken'],
            },
        ).json()
        if (not 'success' in res or not res['success']):
            return HttpResponse('Recaptcha Failure', status = 401)

        # add document to database
        document = Document.objects.create(
            markdown_text = data['text'],
            creator = email,
        )

        # return auto-generated document uuid key to client
        return JsonResponse({'key': str(document.key)})
