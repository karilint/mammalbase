from django.shortcuts import render
from django.http import HttpResponse


def export_hello_world(request):
    print('Hello, world! Greetings from Exports!')
    return HttpResponse('Hello, world! Greetings from Exports!')
