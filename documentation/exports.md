# Exports app

The data export feature has been defined in the `exports` app. This document aims to give a brief explanation on the
different parts of the app that makes the data export possible by the standards given by the owner of the product.


## The query_sets directory

This directory is dedicated to contain QuerySet objects and custom database functions for making Django driven queries
to the database. The documentation for making queries can be found 
[here](https://docs.djangoproject.com/en/3.2/topics/db/queries/). Also read the section **Queries and Fields** to 
understand the passing of the queries around as an argument.


### The measurements query

Allows system to export measurements data in the ETS format. This query has been divided into multiple files in order
to keep the complex query structured and simple. Every query is an extension of the `base_query` to ensure similar data 
in the export requested.


## The ExportFile model

This model is used for recording the data exports made by users of MammalBase. The model is an extension of the 
basemodel defined in the `mb/models.py` module. This basemodel makes the recording possible in the Django
admin system with the `django-simple-history` package without any custom configuration. Note that when executing data
creation tasks in Celery, it is not possible to record user data for the history in the Celery task. Thus, the initial
creation of the model instance must be done in the view function calling the export task, where the information of the 
user can be extracted from the `request` argument. 


## Tasks

The `tasks.py` module contains several functions, but only one is called as a task at the moment. Current implementation
of the data export works in the following way. The `export_to_tsv` function in the `views` module calls the Celery task 
`ets_export_query_set`. This function compiles the query sets according to the arguments given by the caller and calls 
the `export_zip_file` function with the said query sets. The `export_zip_file` function executes the given queries and 
writes the result to a file (one file per one query) and zips the files into one package. The zip package is then
saved to the `ExportFile` model instance and download link is sent to the user via email.


## Queries and Fields

Our implementation of passing query sets around is as follows. Since Django does not hit the database until
`values()` or `values_list()` is called on the query set, we have decided to postpone this call until the result is 
actually written into a file. The `export_zip_file` function takes a list of dictionaries of the form
```
{
    "file_name": str,
    "query_set": QuerySet,
    "fields": tuple[str, str]
}
```
as one of the arguments. This defines the query and the file the result will be written to. The keyword argument 
`fields` is a pair of strings loosely representing the `AS` syntax in SQL. The first string of the pair is the name of 
the requested field in the corresponding Django model and the second string is the desired name for the column printed 
in the first row of the tsv file. To sum up, the pair `('user__name', 'User')` loosely represents the 
`user.name AS User` in SQL.
