from django.shortcuts import render
from django.http import StreamingHttpResponse
from mb.models import ViewMasterTraitValue

import csv

class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """

    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value

def export_to_tsv(request):
    """A view that streams a large TSV file."""
    measurements = ViewMasterTraitValue.objects.all()
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer, delimiter='\t', lineterminator='\n')
    writer.writerow(['id', 'master_id', 'master_entity_name', 'master_attribute_id', 'master_attribute_name', 'traits_references', 'assigned_values', 'n_distinct_value', 'n_value', 'n_supporting_value', 'trait_values', 'trait_selected', 'trait_references', 'value_percentage'])
    msr = measurements.values_list('id', 'master_id', 'master_entity_name', "master_attribute_id", 'master_attribute_name', 'traits_references', 'assigned_values', 'n_distinct_value', 'n_value', 'n_supporting_value', 'trait_values', 'trait_selected', 'trait_references', 'value_percentage')
    return StreamingHttpResponse(
        (writer.writerow(m) for m in msr),
        content_type="text/tsv",
        headers={"Content-Disposition": 'attachment; filename="measurements.tsv"'},
    )  