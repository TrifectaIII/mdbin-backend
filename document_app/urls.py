from django.urls import path

from .views import DocumentView


urlpatterns = [
    path('', DocumentView.as_view(), name = 'DocumentView'),
]
