from django.urls import path

from . import views


urlpatterns = [
    path('get/<identifier>/', views.getDocument, name='getDocument'),
]
