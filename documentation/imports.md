# Imports documentation

### Abstract

The Import Tool is a feature designed to streamline the process of importing data from .tsv files into the system's database. It offers a user-friendly interface where users can upload their .tsv files via a web form. Upon submission, the system performs a series of validations to ensure the integrity and correctness of the provided data. If the validation process succeeds without any errors, the data is imported into the database, and a success message is returned to the user on the web page.

## Usage

Users can upload their .tsv files using the provided web form. The system checks the validity of the uploaded .tsv file to ensure that it meets the required format and data integrity standards.
If the validation process completes successfully, the system proceeds to import the data from the .tsv file into the database.
Upon successful import, a confirmation message is displayed to the user on the web page, indicating that the import process has been completed successfully.

## Data Validation

TODO:

## Architecture

The files that handels Import Tools are located behind _app/imports_-directory. The directory contains for example the validation-library that handels data validation. Top level description for Import Tool is describe below:


```mermaid
graph TD;
    "User has selected TSV-FILE to import" --> "Views.py handles the request";
    "Views.py handles the request" --> "It also initialize the validator and importer";
    "It also initialize the validator and importer" --> "After these operations we call views wrapper";
    "After these operations we call views wrapper" --> "Views wrapper validates TSV-FILE line by line";
    "Views wrapper validates TSV-FILE line by line" --> "If the validator detects format error in the file";
    "If the validator detects format error in the file" --> "It returns to user specific information of the error";
    "If the validator detects format error in the file" --> "IF all the lines are validated successfully";
    "IF all the lines are validated successfully" --> "System starts to import the data to the database";
    "System starts to import the data to the database" --> "The importing scripts are located behind imports-directory";
    "The importing scripts are located behind imports-directory" --> "Every importing data has their own importer";
    "Every importing data has their own importer" --> "The importer adds possible source locations and references is needed";



```
