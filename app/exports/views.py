from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound, FileResponse
from exports.models import ExportFile
from .tasks import ets_export_query_set
from .forms import ETSForm
from mb.views import user_is_data_admin_or_contributor, user_is_data_admin_or_owner


@login_required
def export_to_tsv(request):
    """A view that renders  export form."""
    if request.method == 'POST':
        form = ETSForm(request.POST)
        if form.is_valid():
            user_email = request.POST['user_email']
            checkboxes = request.POST.getlist('export_choices')
            export_file = ExportFile(file=None)
            export_file.save()
            export_file_id = export_file.pk
            is_admin_or_contributor = user_is_data_admin_or_contributor(request.user)
            ets_export_query_set.delay(user_email, export_file_id, is_admin_or_contributor, checkboxes)
            return redirect('submission')
    else:
        form = ETSForm()
    context = {'form': form}
    return render(request, 'export/export_ets.html', context)


def form_submitted(request):
    return render(request,'export/form_submitted.html')


def user_has_rights_to_export_file(user, export_file_object):
    return user.groups.filter(name='data_admin').exists() or export_file_object.created_by == user


@login_required
def get_exported_file(request, file_id):
    try:
        file_object = ExportFile.objects.filter(id=file_id)[0]

        if user_has_rights_to_export_file(request.user, file_object):
            f = file_object.file.open()
            return FileResponse(f, as_attachment=True)
        else:
            raise PermissionDenied

    except IOError:
        return HttpResponseNotFound('<h1>File does not exist</h1>')
    except IndexError:
        return HttpResponseNotFound('<h1>File does not exist</h1>')
