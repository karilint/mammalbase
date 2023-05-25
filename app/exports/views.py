from django.shortcuts import render
from django.http import StreamingHttpResponse

import csv

class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """

    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


def export_to_tsv(request):
    """A view that streams a large CSV file."""
    rows = (["Row {}".format(idx), str(idx)] for idx in range(10))
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    return StreamingHttpResponse(
        (writer.writerow(row) for row in rows),
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="mammalbase.csv"'},
    )  