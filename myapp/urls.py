from django.urls import path
from .views import index, start_recording

urlpatterns = [
    path('start-recording/', start_recording, name='start_recording'),
    path('', index, name='index'),
]