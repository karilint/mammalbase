from django.shortcuts import render


def export_hello_world(request):
    return render(request, "export/export_hello.html")
