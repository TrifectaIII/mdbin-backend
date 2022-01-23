from django.urls import path

from . import views


urlpatterns = [
    path('get/<key>/', views.getDocument, name='getDocument'),
    path('create/', views.createDocument, name='createDocument')
]
