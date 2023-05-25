from django.shortcuts import render
from . import tasks


def export_hello_world(request):
    tasks.hello_world_celery.apply_async(countdown=10)
    return render(request, "export/export_hello.html")
