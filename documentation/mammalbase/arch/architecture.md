## Directory Structure
The project directory structure is as follows:

- `.github/`: Contains GitHub-specific files, such as workflows for GitHub Actions.
- `app/`: The main application directory. It contains several subdirectories:
    - `config/`: Configuration files for the application.
    - `exports/`: Files related to exporting data.
    - `imports/`: Files related to importing data.
    - `itis/`: ITIS (Integrated Taxonomic Information System) related files.
    - `main/`: User authentication, user profiles, and other general application features.
    - `mb/`: Main mammalbase application files.
    - `scripts/`: Scripts used in the application.
    - `tdwg/`: TDWG (Taxonomic Databases Working Group) related files.
    - `tests/`: Unit tests for the application.
    - `urls/`: URL handling is centralized here. paths, subpath includes, etc
- `documentation/`: Contains markdown files with documentation about the application, its architecture, testing, environment variables, etc.
- `nginx/`: Configuration files for the Nginx server.

### Subpackages for models, views etc
In place of many module there is subpackage in use. See [Organizing models in a package, Django Documentation](https://docs.djangoproject.com/en/5.0/topics/db/models/#organizing-models-in-a-package) For example `mb.models` have it's own subpackage with `__init__.py` file so all models can be arranged neatly while being imported correctly.
- `<some dir>/__init__.py`: Subpackage initialization module. It should collect all objects for the subpackage via imports.
- `<some dir>/category.py`: Containing objects in named category. Easy to find. Nice and neat.
- `<some dir>/unsorted.py`: File that have unsorted objects. These files are temporary and objects should be rearranged to corresponding categories.

## Detailed description of directories

### /app/
The `app` directory contains the main django application files. The application is divided into several subapplications, each of which contains files related to a specific feature of the application.

### /app/config/
The `config` directory contains configuration files for the application. The `settings.py` file contains the main settings for the application, such as database settings, installed apps, middleware, etc.

### /app/exports/
Documentation for the exports directory can be found in the [exports documentation](documentation/exports.md).


### /app/imports/
Documentation for the imports directory can be found in the [imports documentation](documentation/imports.md).

### /app/itis/
Itis is a directory that contains files related to the ITIS (Integrated Taxonomic Information System) API.

### /app/main/
The `main` directory contains the main application files related to user authentication, user profiles, and other general application features. It contains templates to login with social account orcId.

### /app/mb/
As you may guess "mb" stads for MammalBase. The `mb` directory contains main files related to main MammalBase application. All the `models` related to MammalBase are defined in this directory. Also all the `views` related to MammalBase are defined in this directory.

### /app/scripts/
The `scripts` directory contains scripts used in the deployment of the application. 

`entrypoint.prod.sh` is the entrypoint script for the production server. 

`entrypoint.sh` is the entrypoint script for the development server.

### /app/tdwg/
The `tdwg` directory contains Taxon model that follows TDWG (Taxonomic Databases Working Group) standards.

### /app/tests/
The `tests` directory contains unit tests for the application. The tests are divided into several folders, each of which contains tests for a specific part of the application. More about testing can be read from [Testing Documentation](testing.md).

### /app/urls/
This subpackage contains all URL related information. All the urls and their
view counterparts are listed in the submodules starting from `__init__.py`.

### /documentation/
This is current directory. The `documentation` directory contains markdown files with documentation about the application.

### /nginx/
The `nginx` directory contains configuration files for the Nginx server.

### /.github/
The `.github` directory contains GitHub-specific files, such as workflows for GitHub Actions.
