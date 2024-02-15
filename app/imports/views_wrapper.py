import logging
import pandas as pd

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse

from utils.views import render	# MB Utils
from .tools import messages

def wrapper(request, validator, importer, path):
    if request.method == "GET":
        print(f"import/{path}.html")
        return render(request, f"import/{path}.html")
    
    try:
        csv_file = request.FILES["csv_file"]
        df = pd.read_csv(csv_file, sep='\t')

        importing_errors = []
        success_rows = 0
        message = None

        headers = list(df.columns.values)
        data = validator.data

        for row in df.itertuples(index=False):
            for i, x in enumerate(row):
                data[headers[i]] = x

            isvalid = validator.is_valid(data, validator.rules)
            errors = validator.errors

            if not isvalid:
                messages.error(request,"Unable to upload file. "+ str(errors))
                return HttpResponseRedirect(reverse(path))

            created = importer.importRow(row, importing_errors)

            if created:
                success_rows += 1

        if success_rows == 0:
            message = "0 rows of data were imported"
        elif len(importing_errors) > 0 and success_rows > 0:
            message = str(success_rows) + " rows of data were imported successfully with some errors in these rows: "

            for error in importing_errors:
                message = message + error
        else:
            message = "File imported successfully. "+ str(df.shape[0])+ " rows of data were imported."

        messages.add_message(request, 50, message, extra_tags="import-message")
        messages.add_message(request, 50, df.to_html(), extra_tags="show-data")
        return HttpResponseRedirect(reverse(path))

    except Exception as e:
        logging.getLogger("error_logger").error("Unable to upload file due to a coding error. "+repr(e))
        messages.error(request, "Unable to upload file. "+repr(e))
        return HttpResponseRedirect(reverse(path))