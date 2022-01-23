from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from . import models


def getDocument(request, identifier):
    document = get_object_or_404(models.Document, identifier=identifier)
    return JsonResponse({
        'markdown_text': document.markdown_text,
        'published': document.published,
    })

# def createDocument(request):
