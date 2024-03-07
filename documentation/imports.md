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
flowchart LR;
  USER HAS SELECTED TSV-FILE TO IMPORT-->VIEWS.PY HANDLES THE REQUEST. IT ALSO INITIALIZE THE VALIDATOR AND IMPORTER. AFTER THESE OPERATIONS WE CALL VIEWS WRAPPER --> VIEWS WRAPPER VALIDATES TSV-FILE LINE BY LINE. IF THE VALIDATOR DETECTS FORMAT ERROR IN THE FILE, IT RETURNS TO USER SPECIFIC INFORMATION OF THE ERROR. --> IF ALL THE LINES ARE VALIDATED SUCCESSFULLY, SYSTEM STARTS TO IMPORT THE DATA TO THE DATABASE. THE IMPORTING SCRIPTS ARE LOCATED BEHIND IMPORTS-DIRECTORY. EVERY IMPORTING DATA HAS THEIR OWN IMPORTER (OCCURRENCES, ETS...). THE IMPORTER ADDS POSSIBLE SOURCE LOCATIONS AND REFERENCES IS NEEDED.
```
