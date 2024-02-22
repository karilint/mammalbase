import logging
import pandas as pd

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse

from utils.views import render	# MB Utils
from .tools import messages

def wrapper(request, validator, importer, path):
    """Wrapper for differnt viewers. 

    Args:
        request (_type_): HTTP-request
        validator (Occurrence_validation): Occurrence_validation object.
        importer (OccurrencesImporter): OccurrenceImporter object
        path (str): The path of the html template to be returned.

    Returns:
        HTTP-response: html-template
    """
    if request.method == "GET":
        print(f"import/{path}.html")
        return render(request, f"import/{path}.html")
    
    csv_file = request.FILES["csv_file"]
    df = pd.read_csv(csv_file, sep='\t')
    try: 
        errors = validate(df, validator)
        if len(errors) > 0:
            for error in errors:
                messages.error(request, error)
            return HttpResponseRedirect(reverse(path))

        rows_imported = row_importer(df, importer)
        if rows_imported > 0:
            message = f"File imported successfully. {rows_imported} rows of data were imported."
            messages.add_message(request, 50, message, extra_tags="import-message")
            messages.add_message(request, 50, df.to_html(), extra_tags="show-data")
            return HttpResponseRedirect(reverse(path))

        else:
            message = f"File failed to import. {rows_imported} rows of data were imported."
            messages.error(request, message)
            return HttpResponseRedirect(reverse(path))

    except Exception as e:
        logging.getLogger("error_logger").error("Unable to upload file due to error. "+repr(e))
        print(e)
        messages.error(request, "Unable to upload file. "+repr(e))
        return HttpResponseRedirect(reverse(path))



def validate(df, validator):
    """Validate rows in tsv-file.

    Args:
        df (Pandas): Pandas-object
        validator (Occurrence-validation): validation object for occurrences

    Returns:
        list: possible validation errors
    """
    importing_errors = []
    headers = list(df.columns.values)
    data = validator.data
    for row in df.itertuples(index=False):
        for i, x in enumerate(row):
            data[headers[i]] = x

        check_valid = validator.is_valid(data, validator.rules)
        errors = validator.errors

        if not check_valid:
            for x in errors:
                importing_errors.append("Error on row: " + str(row) + " Error: " + (x))

        return importing_errors


def row_importer(df, importer):
    """Import validated rows to db.

    Args:
        df (Pandas): Pandas-object
        importer (Occurrence_importer): importer object for occurrences

    Returns:
        int: how many rows was impoerted
    """
    success_rows = 0

    for row in df.itertuples(index=False):
        created = importer.importRow(row)

        if created:
            success_rows += 1
    return success_rows