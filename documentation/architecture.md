## Directory Structure

The project directory structure is as follows:

- `.github/`: Contains GitHub-specific files, such as workflows for GitHub Actions.
- `app/`: The main application directory. It contains several subdirectories:
    - `config/`: Configuration files for the application.
    - `exports/`: Files related to exporting data.
    - `imports/`: Files related to importing data.
    - `itis/`: ITIS (Integrated Taxonomic Information System) related files.
    - `main/`: Main application files.
    - `mb/`: Main application files.
    - `scripts/`: Scripts used in the application.
    - `tdwg/`: TDWG (Taxonomic Databases Working Group) related files.
    - `tests/`: Unit tests for the application.
- `documentation/`: Contains markdown files with documentation about the application, its architecture, testing, environment variables, etc.
- `nginx/`: Configuration files for the Nginx server.

## App

The `app` directory contains the main django application files. The application is divided into several subapplications, each of which contains files related to a specific feature of the application.

### Config

The `config` directory contains configuration files for the application. The `settings.py` file contains the main settings for the application, such as database settings, installed apps, middleware, etc. The `urls.py` file contains the URL patterns for the application.

### Exports

Documentation for the exports directory can be found in the [exports documentation](documentation/exports.md).


### Imports

Documentation for the imports directory can be found in the [imports documentation](documentation/imports.md).

### Itis

Itis is a directory that contains files related to the ITIS (Integrated Taxonomic Information System) API.

### Main

The `main` directory contains the main application files related to user authentication, user profiles, and other general application features. It contains templates to login with socian account orcId.

### Mb (MammalBase)

The `mb` directory contains main files related to main MammalBase application. All the `models` related to MammalBase are defined in this directory. Also all the `views` and `urls` related to MammalBase are defined in this directory.

### Scripts

The `scripts` directory contains scripts used in the deployment of the application. 

`entrypoint.prod.sh` is the entrypoint script for the production server. 

`entrypoint.sh` is the entrypoint script for the development server.

### Tdwg

The `tdwg` directory contains Taxon model that follows TDWG (Taxonomic Databases Working Group) standards.

### Tests

The `tests` directory contains unit tests for the application. The tests are divided into several folders, each of which contains tests for a specific part of the application.

### Documentation

The `documentation` directory contains markdown files with documentation about the application.

### Nginx

The `nginx` directory contains configuration files for the Nginx server.

### .github

The `.github` directory contains GitHub-specific files, such as workflows for GitHub Actions.
