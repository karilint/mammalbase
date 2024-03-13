import logging
import pandas as pd
 
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render

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
        #author_check = check_author_consistency(df)
        if errors:
            for error in errors:
                messages.error(request, error)
            return HttpResponseRedirect(reverse(path))
        #if not author_check:
            messages.error(request, "Authors need to be consisten. Please make sure each row has your own ORCID")
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
    index = 0
    headers = list(df.columns.values)
    data = validator.data
    for row in df.itertuples(index=False):
        index += 1
        for i, x in enumerate(row):
            data[headers[i]] = x
 
        isvalid = validator.is_valid(data, validator.rules)
        errors = validator.errors
        if not isvalid:
            for x in errors:
                importing_errors.append("Error on row: "+ str(index) + ". Error: " + (x))
 
    if len(importing_errors) > 0:
        return importing_errors
    return []
 
 
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
 
def check_author_consistency(df: pd.DataFrame):
    """Check if every row has the same value for the 'author' column as the first row.
 
    Args:
        df (Pandas DataFrame): DataFrame object representing the TSV data.
 
    Returns:
        bool: True if all authors match the first author, False otherwise.
    """
    first_author = df['author'].iloc[1]  # Get the author value from the first row
    # Compare all author values with the first author
    author_match = (df['author'] == first_author).all()
    return author_match